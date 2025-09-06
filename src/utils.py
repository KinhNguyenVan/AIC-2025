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