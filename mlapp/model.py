import json
from pathlib import Path
import numpy as np
import joblib

def load_schema(schema_path: Path) -> list[str]:
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))

def load_model(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(
            f"ML model not found: {model_path}. Train it: python manage.py train_model --csv dataset.csv"
        )
    return joblib.load(model_path)

def vectorize(features: dict, feature_names: list[str]) -> np.ndarray:
    x = np.zeros((1, len(feature_names)), dtype=np.float32)
    for i, name in enumerate(feature_names):
        x[0, i] = float(features.get(name, 0.0))
    return x

def predict_proba(model, x: np.ndarray) -> float:
    return float(model.predict_proba(x)[0, 1])

def verdict_from_score(score_percent: int) -> str:
    if score_percent >= 70:
        return "malicious"
    if score_percent >= 30:
        return "suspicious"
    return "benign"

def top_feature_contributions(model, x: np.ndarray, feature_names: list[str], top_k: int = 8):
    if hasattr(model, "coef_"):
        contrib = (model.coef_[0] * x[0]).astype(float)
        idxs = np.argsort(np.abs(contrib))[::-1][:top_k]
        return [
            {"feature": feature_names[i], "value": float(x[0, i]), "contribution": float(contrib[i])}
            for i in idxs
        ]

    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_.astype(float)
        contrib = imp * np.abs(x[0])
        idxs = np.argsort(contrib)[::-1][:top_k]
        return [
            {"feature": feature_names[i], "value": float(x[0, i]), "importance": float(imp[i])}
            for i in idxs
        ]

    return []
