from qdrant_client import models
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
load_dotenv()
# from src.search.model import CLIPModel

# embedding = CLIPModel()

# text = """A chef puts fish into a white bowl at the exact moment the last fish falls from the plate, then pours flour into the bowl of fish with chopsticks touching the fish for the first time to mix, and finally tests the temperature of hot oil with chopsticks at the moment they are first lifted out of the oil.
# """

# text_features = embedding.encode_text(text)
qdrant_client =QdrantClient(
    url=os.getenv("IMAGE_QDRANT_URL_2"),
    api_key=os.getenv("IMAGE_QDRANT_API_KEY_2"),
    timeout=60.0   
)
qdrant_client.create_payload_index(
    collection_name="image_clip_vectors",
    field_name="path",
    field_schema=models.PayloadSchemaType.TEXT
)

qdrant_client.delete(
    collection_name="image_clip_vectors",
    points_selector=models.FilterSelector(
        filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="path",
                    match=models.MatchText(text="K11_V020")
                )
            ]
        )
    )
)
# video_ids = ["Keyframes_K01", "Keyframes_K02", "Keyframes_K03", "Keyframes_K04"]
# search_result = qdrant_client.search(
#     collection_name="image_clip_vectors",
#     query_vector=text_features.squeeze().tolist(),
#     limit=100,
#     with_payload=True,
#     query_filter=models.Filter(
#         should=[
#             models.FieldCondition(
#                 key="path",
#                 match=models.MatchText(text=vid)
#             )
#             for vid in video_ids
#         ]
#     ),
#     search_params=models.SearchParams(
#         # hnsw_ef=1000,
#         exact=True
#         ),
#     timeout=60

# )
# for hit in search_result:
#     print(hit.payload, hit.score)

