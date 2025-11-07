
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



mapping_topics = {
    "tin tức": ["K01","K02","K03","K04","K05","K06","K07","K08","K09","K10","K11","K12","K13","K14","K15","K16","K17","K18","K19","K20","L21","L22","L27","L28","L29","L30"], 
    "múa lân": ["L24"],
    "đua xe đạp": ["L23"],
    "dạy học online": ["L25"],
    "chương trình nấu ăn": ["L26"]
}


mapping_topics = {
    "tin tức": ["K01","K02","K03","K04","K05","K06","K07","K08","K09","K10","K11","K12","K13","K14","K15","K16","K17","K18","K19","K20","L21","L22","L27","L28","L29","L30"], 
    "múa lân": ["L24"],
    "đua xe đạp": ["L23"],
    "dạy học online": ["L25"],
    "chương trình nấu ăn": ["L26"]
}


# Mock list (CloudFront)
mock_keys = [
    "Keyframes_L30_a/L30_V001/000000.webp",
    "Keyframes_L30_a/L30_V001/000037.webp",
    "Keyframes_L30_a/L30_V001/000074.webp",
    "Keyframes_L30_a/L30_V001/000075.webp",
    "Keyframes_L30_a/L30_V001/000122.webp",
    "Keyframes_L30_a/L30_V001/000169.webp",
    "Keyframes_L30_a/L30_V001/000170.webp",
    "Keyframes_L30_a/L30_V001/000229.webp",
    "Keyframes_L30_a/L30_V001/000289.webp",
    "Keyframes_L30_a/L30_V001/000290.webp",
    "Keyframes_L30_a/L30_V001/000310.webp",
    "Keyframes_L30_a/L30_V001/000330.webp",
    "Keyframes_L30_a/L30_V001/000331.webp",
    "Keyframes_L30_a/L30_V001/000342.webp",
    "Keyframes_L30_a/L30_V001/000353.webp",
    "Keyframes_L30_a/L30_V001/000354.webp",
    "Keyframes_L30_a/L30_V001/000359.webp",
    "Keyframes_L30_a/L30_V001/000365.webp",
    "Keyframes_L30_a/L30_V001/000366.webp",
    "Keyframes_L30_a/L30_V001/000373.webp",
    "Keyframes_L30_a/L30_V001/000380.webp",
    "Keyframes_L30_a/L30_V001/000381.webp",
    "Keyframes_L30_a/L30_V001/000388.webp",
    "Keyframes_L30_a/L30_V001/000396.webp",
    "Keyframes_L30_a/L30_V001/000397.webp",
    "Keyframes_L30_a/L30_V001/000404.webp",
    "Keyframes_L30_a/L30_V001/000412.webp",
    "Keyframes_L30_a/L30_V001/000413.webp",
    "Keyframes_L30_a/L30_V001/000435.webp",
    "Keyframes_L30_a/L30_V001/000457.webp",
    "Keyframes_L30_a/L30_V001/000458.webp",
    "Keyframes_L30_a/L30_V001/000492.webp",
    "Keyframes_L30_a/L30_V001/000527.webp",
    "Keyframes_L30_a/L30_V001/000528.webp",
    "Keyframes_L30_a/L30_V001/000568.webp",
    "Keyframes_L30_a/L30_V001/000608.webp",
    "Keyframes_L30_a/L30_V001/000609.webp",
    "Keyframes_L30_a/L30_V001/000631.webp",
    "Keyframes_L30_a/L30_V001/000654.webp",
    "Keyframes_L30_a/L30_V001/000655.webp",
    "Keyframes_L30_a/L30_V001/000702.webp",
    "Keyframes_L30_a/L30_V001/000749.webp",
    "Keyframes_L30_a/L30_V001/000750.webp",
    "Keyframes_L30_a/L30_V001/000784.webp",
    "Keyframes_L30_a/L30_V001/000819.webp",
    "Keyframes_L30_a/L30_V001/000820.webp",
    "Keyframes_L30_a/L30_V001/000841.webp",
    "Keyframes_L30_a/L30_V001/000862.webp",
    "Keyframes_L30_a/L30_V001/000863.webp",
    "Keyframes_L30_a/L30_V001/000891.webp",
    "Keyframes_L30_a/L30_V001/000919.webp",
    "Keyframes_L30_a/L30_V001/000920.webp",
    "Keyframes_L30_a/L30_V001/000992.webp",
    "Keyframes_L30_a/L30_V001/001064.webp",
    "Keyframes_L30_a/L30_V001/001066.webp",
    "Keyframes_L30_a/L30_V001/001091.webp",
    "Keyframes_L30_a/L30_V001/001116.webp",
    "Keyframes_L30_a/L30_V001/001117.webp",
    "Keyframes_L30_a/L30_V001/001148.webp",
    "Keyframes_L30_a/L30_V001/001180.webp",
    "Keyframes_L30_a/L30_V001/001181.webp",
    "Keyframes_L30_a/L30_V001/001201.webp",
    "Keyframes_L30_a/L30_V001/001221.webp",
    "Keyframes_L30_a/L30_V001/001222.webp",
    "Keyframes_L30_a/L30_V001/001240.webp",
    "Keyframes_L30_a/L30_V001/001258.webp",
    "Keyframes_L30_a/L30_V001/001259.webp",
    "Keyframes_L30_a/L30_V001/001284.webp",
    "Keyframes_L30_a/L30_V001/001310.webp",
    "Keyframes_L30_a/L30_V001/001311.webp",
    "Keyframes_L30_a/L30_V001/001345.webp",
    "Keyframes_L30_a/L30_V001/001380.webp",
    "Keyframes_L30_a/L30_V001/001381.webp",
    "Keyframes_L30_a/L30_V001/001407.webp",
    "Keyframes_L30_a/L30_V001/001434.webp",
    "Keyframes_L30_a/L30_V001/001435.webp",
    "Keyframes_L30_a/L30_V001/001462.webp",
    "Keyframes_L30_a/L30_V001/001490.webp",
    "Keyframes_L30_a/L30_V001/001491.webp",
    "Keyframes_L30_a/L30_V001/001517.webp",
    "Keyframes_L30_a/L30_V001/001544.webp",
    "Keyframes_L30_a/L30_V001/001545.webp",
    "Keyframes_L30_a/L30_V001/001573.webp",
    "Keyframes_L30_a/L30_V001/001602.webp",
    "Keyframes_L30_a/L30_V001/001603.webp",
    "Keyframes_L30_a/L30_V001/001626.webp",
    "Keyframes_L30_a/L30_V001/001649.webp",
    "Keyframes_L30_a/L30_V001/001650.webp",
    "Keyframes_L30_a/L30_V001/001708.webp",
    "Keyframes_L30_a/L30_V001/001767.webp",
    "Keyframes_L30_a/L30_V001/001768.webp",
    "Keyframes_L30_a/L30_V001/001789.webp",
    "Keyframes_L30_a/L30_V001/001810.webp",
    "Keyframes_L30_a/L30_V001/001811.webp",
    "Keyframes_L30_a/L30_V001/001834.webp",
    "Keyframes_L30_a/L30_V001/001857.webp",
    "Keyframes_L30_a/L30_V001/001858.webp",
    "Keyframes_L30_a/L30_V001/001885.webp",
    "Keyframes_L30_a/L30_V001/001912.webp",
    "Keyframes_L30_a/L30_V001/001913.webp",
    "Keyframes_L30_a/L30_V001/001952.webp",
    "Keyframes_L30_a/L30_V001/001992.webp",
    "Keyframes_L30_a/L30_V001/001993.webp",
    "Keyframes_L30_a/L30_V001/002015.webp",
    "Keyframes_L30_a/L30_V001/002037.webp",
    "Keyframes_L30_a/L30_V001/002038.webp",
    "Keyframes_L30_a/L30_V001/002069.webp",
    "Keyframes_L30_a/L30_V001/002100.webp",
    "Keyframes_L30_a/L30_V001/002101.webp",
    "Keyframes_L30_a/L30_V001/002123.webp",
    "Keyframes_L30_a/L30_V001/002146.webp",
    "Keyframes_L30_a/L30_V001/002147.webp",
    "Keyframes_L30_a/L30_V001/002173.webp",
    "Keyframes_L30_a/L30_V001/002199.webp",
    "Keyframes_L30_a/L30_V001/002200.webp",
    "Keyframes_L30_a/L30_V001/002216.webp",
    "Keyframes_L30_a/L30_V001/002232.webp",
    "Keyframes_L30_a/L30_V001/002233.webp",
    "Keyframes_L30_a/L30_V001/002255.webp",
    "Keyframes_L30_a/L30_V001/002278.webp",
    "Keyframes_L30_a/L30_V001/002279.webp",
    "Keyframes_L30_a/L30_V001/002301.webp",
    "Keyframes_L30_a/L30_V001/002324.webp",
    "Keyframes_L30_a/L30_V001/002325.webp",
    "Keyframes_L30_a/L30_V001/002343.webp",
    "Keyframes_L30_a/L30_V001/002362.webp",
    "Keyframes_L30_a/L30_V001/002364.webp",
    "Keyframes_L30_a/L30_V001/002388.webp",
    "Keyframes_L30_a/L30_V001/002412.webp",
    "Keyframes_L30_a/L30_V001/002413.webp",
    "Keyframes_L30_a/L30_V001/002438.webp",
    "Keyframes_L30_a/L30_V001/002464.webp",
    "Keyframes_L30_a/L30_V001/002465.webp",
    "Keyframes_L30_a/L30_V001/002499.webp",
    "Keyframes_L30_a/L30_V001/002534.webp",
    "Keyframes_L30_a/L30_V001/002535.webp",
    "Keyframes_L30_a/L30_V001/002567.webp",
    "Keyframes_L30_a/L30_V001/002600.webp",
    "Keyframes_L30_a/L30_V001/002601.webp",
    "Keyframes_L30_a/L30_V001/002636.webp",
    "Keyframes_L30_a/L30_V001/002672.webp",
    "Keyframes_L30_a/L30_V001/002673.webp",
    "Keyframes_L30_a/L30_V001/002693.webp",
    "Keyframes_L30_a/L30_V001/002713.webp",
    "Keyframes_L30_a/L30_V001/002714.webp",
    "Keyframes_L30_a/L30_V001/002782.webp",
    "Keyframes_L30_a/L30_V001/002851.webp",
    "Keyframes_L30_a/L30_V001/002852.webp",
    "Keyframes_L30_a/L30_V001/002891.webp",
    "Keyframes_L30_a/L30_V001/002931.webp",
    "Keyframes_L30_a/L30_V001/002932.webp",
    "Keyframes_L30_a/L30_V001/002959.webp",
    "Keyframes_L30_a/L30_V001/002987.webp",
    "Keyframes_L30_a/L30_V001/002989.webp",
    "Keyframes_L30_a/L30_V001/003075.webp",
    "Keyframes_L30_a/L30_V001/003161.webp",
]