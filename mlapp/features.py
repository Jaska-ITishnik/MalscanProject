import re
import math
from collections import Counter
import numpy as np

SUSPICIOUS_KEYWORDS = [
    b"powershell", b"cmd.exe", b"wscript", b"cscript", b"rundll32",
    b"reg add", b"schtasks", b"certutil", b"bitsadmin",
    b"invoke-expression", b"base64", b"frombase64string",
    b"virtualalloc", b"createremotethread", b"loadlibrary",
]

URL_REGEX = re.compile(rb"(https?://[^\s'\"<>]+)", re.IGNORECASE)
IP_REGEX = re.compile(rb"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL_REGEX = re.compile(rb"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    ent = 0.0
    for c in counts.values():
        p = c / length
        ent -= p * math.log2(p)
    return float(ent)

def byte_histogram(data: bytes) -> np.ndarray:
    if not data:
        return np.zeros(256, dtype=np.float32)
    arr = np.frombuffer(data, dtype=np.uint8)
    hist = np.bincount(arr, minlength=256).astype(np.float32)
    hist /= max(1.0, float(hist.sum()))
    return hist

def printable_strings(data: bytes, min_len: int = 4):
    pattern = rb"[\x20-\x7E]{%d,}" % min_len
    return re.findall(pattern, data)

def extract_features(data: bytes, mime_type: str = "") -> tuple[dict, dict]:
    """Return (features, evidence) for any file bytes."""
    size = len(data)
    ent = shannon_entropy(data)

    hist = byte_histogram(data)
    strings = printable_strings(data, min_len=4)
    num_strings = len(strings)
    total_string_bytes = sum(len(s) for s in strings) if strings else 0

    lower = data.lower()

    url_hits = URL_REGEX.findall(lower)
    ip_hits = IP_REGEX.findall(lower)
    email_hits = EMAIL_REGEX.findall(lower)

    suspicious_kw_hits = []
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in lower:
            suspicious_kw_hits.append(kw.decode("utf-8", errors="ignore"))

    high_entropy_flag = 1 if ent >= 7.2 else 0

    features = {
        "size_bytes": float(size),
        "entropy": float(ent),
        "high_entropy_flag": float(high_entropy_flag),
        "num_strings": float(num_strings),
        "total_string_bytes": float(total_string_bytes),
        "url_count": float(len(url_hits)),
        "ip_count": float(len(ip_hits)),
        "email_count": float(len(email_hits)),
        "suspicious_kw_count": float(len(suspicious_kw_hits)),
    }

    for i in range(256):
        features[f"hist_{i}"] = float(hist[i])

    evidence = {
        "mime_type": mime_type,
        "suspicious_keywords": suspicious_kw_hits[:20],
        "urls": [u.decode("utf-8", errors="ignore") for u in url_hits[:20]],
        "ips": [ip.decode("utf-8", errors="ignore") for ip in ip_hits[:20]],
        "emails": [e.decode("utf-8", errors="ignore") for e in email_hits[:20]],
        "entropy": ent,
    }

    return features, evidence
