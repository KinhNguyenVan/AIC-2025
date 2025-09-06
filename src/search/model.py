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
        """
        Initializes the Gemini model and configures the API key.
        The API key is retrieved from the 'GOOGLE_API_KEY' environment variable.
        """
        self.model = None
        self.system_prompt = """

        You are an assistant that rewrites user queries into short, concise English descriptions of objects and actions, optimized for CLIP-based image/video retrieval. 

        Instructions:
        1. Input is a description in Vietnamese or English, possibly containing multiple sequential scenes or actions.
        2. Analyze and extract:
        - Objects (people, items, environments, scenes).
        - Actions (movements, events, state changes).
        - Order of events if given (E1, E2, ...).
        3. Rewrite the input into a single English description (or multiple sentences if needed), keeping only the essential visual objects and actions.
        4. Do not include explanations, metadata, or any additional words — only output the rewritten English query.
        
        Examples:

        Input:
        "Trong đoạn video nấu ăn một món ăn về nấm, gồm các khoảnh khắc sơ chế:
        E1: Khoảnh khắc đầu tiên thấy cắt nấm.
        E2: Khoảnh khắc đầu tiên cắt củ năng.
        E3: Khoảnh khắc đầu tiên cắt đậu hủ.
        E4: Khoảnh khắc chảo đặt lên bếp, đầu bếp mở lửa và thấy lửa bắt đầu xuất hiện."

        Output:
        "E1: a chef cutting mushrooms. 
        E2: a chef cutting water chestnuts. 
        E3: a chef cutting tofu. 
        E4: a chef placing a pan on the stove and lighting the fire."

        ---

        Input:
        "Tìm một đoạn video đua xe đạp, góc quay từ flycam trên cao, một vận động viên mặc áo xanh dương, trắng đang vượt ba vận động viên khác và lên vị trí dẫn đầu. Biết sau đó vận động viên này dẫn đầu suốt đoạn đường còn lại đến đích."

        Output:
        "A drone view of a cycling race. A cyclist in blue and white overtakes three other cyclists and takes the lead."

        Let do it with query: {query}
        
        """
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("Warning: GOOGLE_API_KEY environment variable is not set.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
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
            return response.text
        except Exception as e:
            return f"An error occurred while calling the Gemini API: {e}"

gemini_model = GeminiModel()
clip_embedding = CLIPModel()
bgem3_embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
bm25_embedding = SparseTextEmbedding("Qdrant/bm25")

