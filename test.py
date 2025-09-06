from qdrant_client import models
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
load_dotenv()
qdrant_client =QdrantClient(
    url=os.getenv("IMAGE_QDRANT_URL_1"),
    api_key=os.getenv("IMAGE_QDRANT_API_KEY_1"),
    timeout=60.0   
)
# qdrant_client.create_payload_index(
#     collection_name="image_clip_vectors",
#     field_name="path",
#     field_schema=models.PayloadSchemaType.TEXT
# )

qdrant_client.delete(
    collection_name="image_clip_vectors",
    points_selector=models.FilterSelector(
        filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="path",
                    match=models.MatchText(text="Keyframes_K07/K07_V001")
                )
            ]
        )
    )
)

