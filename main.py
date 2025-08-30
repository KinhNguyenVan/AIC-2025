from src.search.model import CLIPModel
from src.search.qdrant_db import qdrant_client

embedding = CLIPModel()

text = """A chef puts fish into a white bowl at the exact moment the last fish falls from the plate, then pours flour into the bowl of fish with chopsticks touching the fish for the first time to mix, and finally tests the temperature of hot oil with chopsticks at the moment they are first lifted out of the oil.
"""

text_features = embedding.encode_text(text)
search_result = qdrant_client.search(
    collection_name="image_clip_vectors",
    query_vector=text_features.squeeze().tolist(),
    limit=20

)
for hit in search_result:
    print(hit.payload, hit.score)