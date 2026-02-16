import thrember

# where you want to store datasets
apk_dir = "/home/jasurbek/PycharmProjects/MalscanProject/data/ember2024_apk"
pdf_dir = "/home/jasurbek/PycharmProjects/MalscanProject/data/ember2024_pdf"

# APK
thrember.download_dataset(apk_dir, file_type="APK", split="train")
thrember.download_dataset(apk_dir, file_type="APK", split="test")

# PDF
thrember.download_dataset(pdf_dir, file_type="PDF", split="train")
thrember.download_dataset(pdf_dir, file_type="PDF", split="test")

print("Done.")
