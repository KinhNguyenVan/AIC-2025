from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

image_qdrant_client_1 = QdrantClient(
    url=os.getenv("IMAGE_QDRANT_URL_1"),
    api_key=os.getenv("IMAGE_QDRANT_API_KEY_1")
)
content_qdrant_client = QdrantClient(
    url=os.getenv("CONTENT_QDRANT_URL"),
    api_key=os.getenv("CONTENT_QDRANT_API_KEY")
)

image_qdrant_client_2 = QdrantClient(
    url=os.getenv("IMAGE_QDRANT_URL_2"),
    api_key=os.getenv("IMAGE_QDRANT_API_KEY_2")
)
