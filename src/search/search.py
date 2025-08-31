from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http import models

def image_search(text, embedding, qdrant_client):
    text_features = embedding.encode_text(text)
    search_result = qdrant_client.search(
        collection_name="image_clip_vectors",
        query_vector=text_features.squeeze().tolist(),
        limit=500000,
        with_payload=True,
        search_params={"exact":True},
        timeout=60
    )
    results = []
    for hit in search_result:
        payload = hit.payload
        payload['score'] = hit.score
        results.append(payload)
    return results



def content_search(text,bgem3_embedding,bm25_embedding,client):
    query = text

    dense_q = bgem3_embedding.embed_query(query)
    sparse_list = list(bm25_embedding.passage_embed(query))
    sparse_q = models.SparseVector(
            indices=sparse_list[0].indices.tolist(),
            values=sparse_list[0].values.tolist()
        )
    prefetch = [
        models.Prefetch(
            query=dense_q,
            using="bge-m3",
            limit=50,
        ),
        models.Prefetch(
            query=sparse_q,
            using="bm25",
            limit=50,
        ),
    ]
    results = client.query_points(
            "hybrid_content_collection",
            prefetch=prefetch,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
            with_payload=True,
            limit=50,
        )
    video_dict = {}
    for point in results.points:
        score = point.score
        video_name = point.payload.get("video_name", "")
        if video_name not in video_dict or score > video_dict[video_name]:
            video_dict[video_name] = score

    # Convert back to list of dicts and sort by score
    result_list = [{"name": name, "score": score} for name, score in video_dict.items()]
    result_list.sort(key=lambda x: x['score'], reverse=True)

    return result_list