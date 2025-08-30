import os

def rerank_images(image_results, content_results):
    """
    Reranks image results based on content scores.
    New score = image_score + image_score * content_score.
    """
    content_scores = {item['name']: item['score'] for item in content_results}
    
    reranked_results = []
    for img in image_results:
        image_score = img.get("score", 0)
        image_path = img.get("path", "")
        
        # Extract video name from image_path (e.g., 'L30_V064' from 'Keyframes_L30_a/L30_V064/001274.webp')
        try:
            video_name = os.path.normpath(image_path).split(os.sep)[-2]
        except IndexError:
            video_name = None

        content_score = content_scores.get(video_name, 0)
        
        # Apply reranking formula
        new_score = image_score + (image_score * content_score)
        
        reranked_img = img.copy()
        reranked_img["score"] = new_score
        reranked_results.append(reranked_img)
        
    # Sort by the new score in descending order
    reranked_results.sort(key=lambda x: x['score'], reverse=True)
    
    return reranked_results
