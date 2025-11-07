import torch
import open_clip
from PIL import Image
from langchain_huggingface import HuggingFaceEmbeddings
from fastembed import SparseTextEmbedding
import os
import google.generativeai as genai


device='cuda' if torch.cuda.is_available() else 'cpu'


class CLIPModel:
    def __init__(self):
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-SO400M-14-SigLIP-384', pretrained='webli')
        self.tokenizer = open_clip.get_tokenizer('ViT-SO400M-14-SigLIP-384')
    def encode_image(self, image_path):
        image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()

    def encode_text(self, text):
        text_tokens = self.tokenizer([text]).to(device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy()
    
class GeminiModel:
    """
    A class to interact with the Google Gemini API.
    """
    def __init__(self):
        self.system_prompt = """
        You are an assistant. Follow the JSON-prompt spec below and rewrite the query.
        {
            "role": "system",
            "task": "Rewrite user queries into enriched but general English descriptions of objects, actions, and camera movements, optimized for CLIP-based image/video retrieval.",
            "instructions": {
                "input_format": "A description in Vietnamese or English, possibly containing multiple sequential scenes or actions.",
                "steps": [
                "1. Analyze and extract key visual elements:",
                "   - Objects: people, items, environments, and scenes.",
                "   - Actions: movements, events, state changes.",
                "   - Camera movements: zoom, pan, tilt, tracking, aerial shots, etc.",
                "   - Order of events if given (E1, E2, ...).",
                "2. Enrich the description but stay general:",
                "   - Add layout, arrangement, motion, and scene transitions.",
                "   - Describe visible actions and camera perspectives (close-up, wide shot, panning, aerial view).",
                "   - Do not infer hidden details (e.g., do not assume the type of bread, cheese, or dessert unless explicitly stated).",
                "   - Keep colors, objects, and actions in general form (e.g., use 'blue/green' instead of guessing exact shade, use 'a pastry' instead of 'baked croissant').",
                "3. Rewrite into concise but enriched English sentences with general details.",
                "4. Do not include explanations, metadata, or commentary — only output the rewritten query."
                ],
                "output_format": "English sentences, one per event or scene, enriched with general but clear visual and camera details."
            },
            "examples": [
                {
                "input": "Cảnh quay nhiều người đứng quanh một cột đá có các số 10, 12, 14, 16, 18, 20. Sau đó máy quay chuyển sang cảnh một người đứng trên cầu nhìn xuống dòng sông chảy xiết.",
                "output": "E1: a group of people gathered around a stone pillar with numbers carved on it. Wide shot with camera slowly panning across the crowd. E2: a person standing on a bridge, camera angle from behind showing a fast-flowing river below."
                },
                {
                "input": "Tìm một đoạn video đua xe đạp, góc quay từ flycam trên cao, một vận động viên mặc áo xanh dương, trắng đang vượt ba vận động viên khác và lên vị trí dẫn đầu. Biết sau đó vận động viên này dẫn đầu suốt đoạn đường còn lại đến đích.",
                "output": "Aerial drone shot of a cycling race. A cyclist in blue and white overtakes three riders from above, moves into the lead, and remains ahead until reaching the finish line."
                }
            ],
            "query_placeholder": "{query}"
        }
        """
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("Warning: GOOGLE_API_KEY environment variable is not set.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")

    def generate_content(self, query: str):
        """
        Generates text content using the Gemini 2.5 Flash model.

        Args:
            query (str): The text prompt to send to the model.

        Returns:
            str: The generated text from the model, or an error message.
        """
        if not self.model:
            return "Gemini model is not initialized. Please check your API key and configuration."
        
        try:
            prompt = self.system_prompt.replace("{query}", query)
            response = self.model.generate_content(prompt)
            print(response.text)
            return response.text
        except Exception as e:
            return f"An error occurred while calling the Gemini API: {e}"

gemini_model = GeminiModel()
clip_embedding = CLIPModel()
bgem3_embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
bm25_embedding = SparseTextEmbedding("Qdrant/bm25")

