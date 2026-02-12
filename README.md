# MalScan (Django 6.0, Class-Based Views)

ML-based static malware analysis web app (no registration).

## Install (Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo apt-get install -y libmagic1
```

## Migrate DB
```bash
python manage.py makemigrations
python manage.py migrate
```

## Train ML model
Create `dataset.csv` with columns: `path,label` (label 0=benign, 1=malicious), then:
```bash
python manage.py train_model --csv dataset.csv
```

This will create:
- `artifacts/model.joblib`
- `artifacts/feature_schema.json`

## Run
```bash
python manage.py runserver 0.0.0.0:8000
```

Open: `http://SERVER_IP:8000/`

## Notes
- Files are never executed.
- This MVP uses generic static features (entropy, strings, URL/IP counts, byte histogram).
- Add file-type plugins (PE/PDF/Office) later for better accuracy.
