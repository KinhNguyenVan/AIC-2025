import os
from collections import defaultdict
from src.utils import deduplicate_and_sort


def rerank_images(image_results, content_results):
    """
    Rerank image results by grouping frames by video.
    - First sort videos by content_score (descending).
    - Then, within each video group, sort frames by image_score (descending).
    """

    # Map: video_name -> content_score
    content_scores = {item['name']: item['score'] for item in content_results}

    # Sắp xếp nội dung theo điểm số giảm dần
    image_results = deduplicate_and_sort(image_results, payload_key="path")
    print(image_results)

    # Nhóm frames theo video
    video_groups = defaultdict(list)
    for img in image_results:
        image_score = img.get("score", 0)
        image_path = img.get("path", "")

        # Lấy tên video (vd: "L30_V064")
        try:
            video_name = os.path.normpath(image_path).split(os.sep)[-2]
        except IndexError:
            video_name = None

        video_groups[video_name].append(img)

    # Sắp xếp video theo content_score giảm dần
    sorted_videos = sorted(
        video_groups.keys(),
        key=lambda v: content_scores.get(v, 0),
        reverse=True
    )

    # Rerank kết quả
    reranked_results = []
    for v in sorted_videos:
        frames = video_groups[v]
        # Sắp xếp các frame trong video theo image_score giảm dần
        frames_sorted = sorted(frames, key=lambda x: x.get("score", 0), reverse=True)
        reranked_results.extend(frames_sorted)

    return reranked_results