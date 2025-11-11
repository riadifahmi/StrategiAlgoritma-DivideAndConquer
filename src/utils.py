# src/utils.py
import re
import math

def clean_text(s: str) -> str:
    """
    Hapus karakter kontrol, emoji & simbol aneh sederhana,
    ubah ke lower case, normalisasi spasi.
    """
    if s is None:
        return ""
    s = str(s)
    # hilangkan emoji/karakter non-word sederhana (unicode range)
    # remove most emojis and other non printable characters
    s = re.sub(r'[\U00010000-\U0010ffff]', '', s)  # high-plane chars (many emojis)
    s = re.sub(r'[\r\n\t]', ' ', s)
    s = re.sub(r'[^\x00-\x7F\u00C0-\u024F0-9a-zA-Z\s\-\']', ' ', s)  # keep basic latin + latin1 ext
    s = s.lower()
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Hitung jarak (km) antara dua koordinat (haversine).
    """
    R = 6371.0  # km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
