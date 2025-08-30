from src.search.model import CLIPModel
from src.search.qdrant_db import qdrant_client

embedding = CLIPModel()
text = """This is the prize introduction for a contest designed with a blue background and white text overlaid on the contest introduction video. There are 18 main prizes in total for the contest. What is the total value of the main prizes?"""

text_features = embedding.encode_text(text)
search_result = qdrant_client.search(
    collection_name="image_clip_vectors",
    query_vector=text_features.squeeze().tolist(),
    limit=10
)
for hit in search_result:
    print(hit.payload, hit.score)