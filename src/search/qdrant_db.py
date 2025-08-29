from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY")
)
