from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

image_qdrant_client = QdrantClient(
    url=os.getenv("IMAGE_QDRANT_URL"),
    api_key=os.getenv("IMAGE_QDRANT_API_KEY")
)
content_qdrant_client = QdrantClient(
    url=os.getenv("CONTENT_QDRANT_URL"),
    api_key=os.getenv("CONTENT_QDRANT_API_KEY")
)
