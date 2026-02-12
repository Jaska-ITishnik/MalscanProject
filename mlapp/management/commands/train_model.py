import json
from pathlib import Path
import csv

from django.core.management.base import BaseCommand
from django.conf import settings

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
import joblib

class Command(BaseCommand):
    help = "Train ML model from CSV with columns: path,label (label 0/1)."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Dataset CSV with columns: path,label")
        parser.add_argument("--test_size", type=float, default=0.2)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **opts):
        csv_path = Path(opts["csv"]).resolve()
        if not csv_path.exists():
            raise FileNotFoundError(csv_path)

        from mlapp.features import extract_features
        import magic

        rows = []
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)

        if not rows:
            self.stdout.write(self.style.ERROR("Empty dataset CSV"))
            return

        # Build feature schema from first sample
        first_path = Path(rows[0]["path"])
        data0 = first_path.read_bytes()
        try:
            mime0 = magic.from_file(str(first_path), mime=True) or ""
        except Exception:
            mime0 = ""
        feats0, _ = extract_features(data0, mime0)
        feature_names = sorted(feats0.keys())

        def vectorize(feats: dict) -> np.ndarray:
            return np.array([float(feats.get(k, 0.0)) for k in feature_names], dtype=np.float32)

        X_feats = []
        y = []

        for r in rows:
            p = Path(r["path"])
            label = int(r["label"])
            if not p.exists():
                self.stdout.write(self.style.WARNING(f"Missing file: {p}"))
                continue

            data = p.read_bytes()
            try:
                mime = magic.from_file(str(p), mime=True) or ""
            except Exception:
                mime = ""

            feats, _ = extract_features(data, mime)
            X_feats.append(vectorize(feats))
            y.append(label)

        if len(y) < 10:
            self.stdout.write(self.style.ERROR("Not enough samples. Need at least ~10."))
            return

        X = np.stack(X_feats)
        y = np.array(y, dtype=np.int32)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=opts["test_size"], random_state=opts["seed"],
            stratify=y if len(set(y)) > 1 else None
        )

        model = RandomForestClassifier(
            n_estimators=400,
            random_state=opts["seed"],
            n_jobs=-1,
            class_weight="balanced_subsample",
        )
        model.fit(X_train, y_train)

        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)

        auc = None
        try:
            auc = roc_auc_score(y_test, proba)
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS("Training done. Evaluation:"))
        self.stdout.write(classification_report(y_test, pred, digits=4))
        if auc is not None:
            self.stdout.write(self.style.SUCCESS(f"ROC-AUC: {auc:.4f}"))

        settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, settings.ML_MODEL_PATH)
        settings.ML_SCHEMA_PATH.write_text(json.dumps(feature_names, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Saved model: {settings.ML_MODEL_PATH}"))
        self.stdout.write(self.style.SUCCESS(f"Saved schema: {settings.ML_SCHEMA_PATH}"))
