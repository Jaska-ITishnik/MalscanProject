from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Download EMBER2024 subsets (APK+PDF) into given directories."

    def add_arguments(self, parser):
        parser.add_argument("--apk_dir", required=True)
        parser.add_argument("--pdf_dir", required=True)

    def handle(self, *args, **opts):
        import thrember

        apk_dir = opts["apk_dir"]
        pdf_dir = opts["pdf_dir"]

        self.stdout.write(self.style.WARNING("Downloading APK train/test..."))
        thrember.download_dataset(apk_dir, file_type="APK", split="train")
        thrember.download_dataset(apk_dir, file_type="APK", split="test")

        self.stdout.write(self.style.WARNING("Downloading PDF train/test..."))
        thrember.download_dataset(pdf_dir, file_type="PDF", split="train")
        thrember.download_dataset(pdf_dir, file_type="PDF", split="test")

        self.stdout.write(self.style.SUCCESS("Done."))
