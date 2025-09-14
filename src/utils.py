
import numpy as np

def deduplicate_and_sort(image_results, payload_key="path"):
    """
    Xóa bớt các point có cùng payload_key (giữ lại point có score cao nhất),
    rồi sắp xếp lại theo score giảm dần.
    """
    unique = {}

    for point in image_results:
        # Vì point là dict flatten, lấy trực tiếp
        payload_value = point.get(payload_key)
        score = point.get("score", 0)

        if payload_value is None:
            continue

        if (payload_value not in unique) or (score > unique[payload_value]["score"]):
            unique[payload_value] = point

    deduped_results = sorted(unique.values(), key=lambda x: x["score"], reverse=True)


    return deduped_results


def normalize_scores(results):
    scores = [item["score"] for item in results]
    if not scores:  # tránh chia cho 0
        return results
    min_s, max_s = min(scores), max(scores)
    if min_s == max_s:
        return results  # tất cả bằng nhau, khỏi normalize
    return [
        {"path": item["path"], "score": (item["score"] - min_s) / (max_s - min_s)}
        for item in results
    ]

