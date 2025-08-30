import torch
import open_clip
from PIL import Image
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