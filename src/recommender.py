# src/recommender.py
from typing import List, Dict, Any, Tuple
import numpy as np
from utils import clean_text, haversine_distance
import math

# Konfigurasi bobot / threshold default
DEFAULTS = {
    "chunk_size": 50,      # ukuran leaf sebelum filter langsung
    "weight_name": 2.0,
    "weight_review": 1.0,
    "weight_rating": 1.2,
    "max_distance_km": 100.0,   # batas default (bisa override)
    "min_rating": 0.0,
}

def tokenize(text: str):
    if not text:
        return []
    return text.split()

def relevance_score(item_name: str, reviews_text: str, query_tokens: List[str]) -> float:
    """
    Sederhana: hitung kecocokan berdasarkan token intersection dan frekuensi,
    beri bobot lebih untuk kemunculan di name daripada di reviews.
    """
    name_tokens = tokenize(item_name)
    review_tokens = tokenize(reviews_text)

    # counts
    name_count = sum(1 for t in name_tokens for q in query_tokens if q in t)
    review_count = sum(1 for t in review_tokens for q in query_tokens if q in t)

    # normalisasi berdasarkan panjang teks
    name_norm = name_count / max(1, len(name_tokens))
    review_norm = review_count / max(1, len(review_tokens))

    score = DEFAULTS["weight_name"] * name_norm + DEFAULTS["weight_review"] * review_norm
    return score

def normalize_distance_score(dist_km: float, max_dist=DEFAULTS["max_distance_km"]) -> float:
    """
    Konversi jarak menjadi skor 0..1, semakin dekat -> semakin tinggi.
    Gunakan fungsi invers (1 - dist/max), dengan floor di 0.
    """
    d = min(dist_km, max_dist)
    score = 1.0 - (d / max_dist)
    return max(0.0, score)

def make_item_score(item: Dict[str, Any], user_lat: float, user_lng: float, query_tokens: List[str], max_distance_km: float, min_rating: float) -> Tuple:
    """
    Kembalikan tuple kunci untuk sorting (relevansi desc, rating desc, distance asc),
    plus skor gabungan (bisa dipakai untuk threshold).
    """
    # hitung jarak
    lat = item.get("lat")
    lng = item.get("lng")
    dist = math.inf
    if lat is not None and lng is not None:
        try:
            dist = haversine_distance(user_lat, user_lng, float(lat), float(lng))
        except:
            dist = math.inf

    # apabila melewati filter sederhana: rating dan distance
    rating = item.get("rating")
    try:
        rating_f = float(rating) if rating not in (None, "", "nan") else 0.0
    except:
        rating_f = 0.0

    # relevansi
    name = clean_text(item.get("name", ""))
    reviews_text = clean_text(item.get("reviews_text", "") or "")
    rel = relevance_score(name, reviews_text, query_tokens)

    # distance score untuk scoring gabungan
    dist_score = normalize_distance_score(dist, max_distance_km)

    # skor gabungan (opsional)
    combined = rel * 100 + DEFAULTS["weight_rating"] * rating_f * 10 + dist_score * 5

    # kunci sort: (neg relevansi -> lebih besar relevansi di atas, neg rating, distance)
    return ((-rel, -rating_f, dist), combined, {
        "name": item.get("name"),
        "address": item.get("address", item.get("formatted_address", "")),
        "rating": rating_f,
        "distance_km": round(dist, 3) if dist != math.inf else None,
        "opening_hours": item.get("time", item.get("opening_hours", None)),
        "types": item.get("types", ""),
        "combined_score": combined
    })

def filter_leaf(items: List[Dict[str, Any]], user_lat: float, user_lng: float, query_tokens: List[str], max_distance_km: float, min_rating: float) -> List[Tuple]:
    """
    Proses satu leaf (non-recursive): filter & scoring, kembalikan list terurut
    berupa tuples (sort_key_tuple, combined_score, result_dict)
    """
    results = []
    for itm in items:
        # cek rating minimal
        rating = itm.get("rating")
        try:
            rating_f = float(rating) if rating not in (None, "", "nan") else 0.0
        except:
            rating_f = 0.0
        # hitung distance quickly
        lat = itm.get("lat"); lng = itm.get("lng")
        if lat is None or lng is None:
            dist = float('inf')
        else:
            try:
                dist = haversine_distance(user_lat, user_lng, float(lat), float(lng))
            except:
                dist = float('inf')

        # reject by rating/distance constraints early
        if rating_f < min_rating:
            continue
        if dist > max_distance_km:
            continue

        sort_key, combined, result = make_item_score(itm, user_lat, user_lng, query_tokens, max_distance_km, min_rating)
        # hanya include yang relevansi > 0 atau ada mention token (jika query non-empty)
        if sum(1 for q in query_tokens if q in (clean_text(itm.get("name","")) + " " + clean_text(itm.get("reviews_text","")))) == 0 and len(query_tokens)>0:
            # skip non-matching
            continue
        results.append((sort_key, combined, result))

    # sort results by sort_key
    results.sort(key=lambda x: x[0])
    return results

def merge_sorted_lists(a: List[Tuple], b: List[Tuple], top_k: int = None) -> List[Tuple]:
    """
    Merge dua list yang sudah terurut (menurut sort_key) -> like merge step pada merge sort.
    """
    i = j = 0
    merged = []
    while (i < len(a) or j < len(b)) and (top_k is None or len(merged) < top_k):
        if i >= len(a):
            merged.append(b[j]); j += 1; continue
        if j >= len(b):
            merged.append(a[i]); i += 1; continue
        # compare sort_key (they are tuples with negative signs for desc)
        if a[i][0] <= b[j][0]:
            merged.append(a[i]); i += 1
        else:
            merged.append(b[j]); j += 1
    return merged

def divide_and_conquer(items: List[Dict[str, Any]], user_lat: float, user_lng: float,
                       query: str, max_distance_km: float = DEFAULTS["max_distance_km"],
                       min_rating: float = DEFAULTS["min_rating"],
                       chunk_size: int = DEFAULTS["chunk_size"],
                       top_k: int = 20) -> List[Dict]:
    """
    Implementasi Divide & Conquer:
    - jika jumlah items <= chunk_size: proses leaf (filter + scoring)
    - else: bagi dua, panggil rekursif, lalu merge hasil terurutnya.
    Kembalikan list hasil (result dict) terurut.
    """
    query_clean = clean_text(query)
    query_tokens = query_clean.split() if query_clean else []

    def _dac(sub_items: List[Dict[str, Any]]) -> List[Tuple]:
        n = len(sub_items)
        if n == 0:
            return []
        if n <= chunk_size:
            # proses langsung
            return filter_leaf(sub_items, user_lat, user_lng, query_tokens, max_distance_km, min_rating)
        mid = n // 2
        left = _dac(sub_items[:mid])
        right = _dac(sub_items[mid:])
        merged = merge_sorted_lists(left, right, top_k=top_k)
        return merged

    scored = _dac(items)
    # ambil top_k dan keluarkan result dict
    final = [r[2] for r in scored[:top_k]]
    return final
