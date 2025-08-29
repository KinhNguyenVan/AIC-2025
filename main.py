from src.search.model import CLIPModel
from src.search.qdrant_db import qdrant_client

embedding = CLIPModel()
text = """Một người đàn ông mặc vest xanh, 
áo sơ mi trắng và cà vạt đỏ đang đứng trước bảng trắng/khung 
nền có nhiều công thức toán học"""

text_features = embedding.encode_text([text])
search_result = qdrant_client.search(
    collection_name="image_clip_vectors",
    query_vector=text_features[0].tolist(),
    limit=10
)
for hit in search_result:
    print(hit.payload, hit.score) 