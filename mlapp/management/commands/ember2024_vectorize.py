from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Vectorize EMBER2024 raw features into X_*.dat / y_*.dat for APK+PDF (skip challenge if missing)."

    def add_arguments(self, parser):
        parser.add_argument("--apk_dir", required=True)
        parser.add_argument("--pdf_dir", required=True)
        parser.add_argument("--label_type", default="label")

    def _has_vectorized(self, data_dir: str) -> bool:
        p = Path(data_dir)
        return all((p / name).exists() for name in ("X_train.dat", "y_train.dat", "X_test.dat", "y_test.dat"))

    def _safe_vectorize(self, thrember, data_dir: str, label_type: str, title: str):
        # Если уже есть .dat — можно не делать заново
        if self._has_vectorized(data_dir):
            self.stdout.write(self.style.SUCCESS(f"{title}: already vectorized (X_/y_ .dat exist)"))
            return

        self.stdout.write(self.style.WARNING(f"Vectorizing {title} ({label_type})..."))

        try:
            thrember.create_vectorized_features(data_dir, label_type=label_type)
            self.stdout.write(self.style.SUCCESS(f"{title}: vectorization complete"))
            return

        except ValueError as e:
            # thrember падает если нет challenge jsonl
            msg = str(e)
            if "Did not find any .jsonl files" not in msg:
                raise

            # train/test уже могли успеть создаться; просто продолжаем
            if self._has_vectorized(data_dir):
                self.stdout.write(self.style.WARNING(
                    f"{title}: challenge split not found, but train/test vectorized OK — skipping challenge."
                ))
                return

            # если даже train/test не создались — значит проблема не только в challenge
            raise

    def handle(self, *args, **opts):
        import thrember

        label_type = opts["label_type"]
        self._safe_vectorize(thrember, opts["apk_dir"], label_type, "APK")
        self._safe_vectorize(thrember, opts["pdf_dir"], label_type, "PDF")
        self.stdout.write(self.style.SUCCESS("Vectorize step finished."))
