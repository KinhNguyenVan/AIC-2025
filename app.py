from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import random
import json

from sympy import limit
from s3.s3_utils import get_neighbor_frames  # import hàm có sẵn
from src.search.model import CLIPModel
from src.search.qdrant_db import image_qdrant_client, content_qdrant_client
from src.search.search import image_search, content_search
from src.rerank.rerank import rerank_images
from langchain_huggingface import HuggingFaceEmbeddings
from fastembed import SparseTextEmbedding


clip_embedding = CLIPModel()
bgem3_embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
bm25_embedding = SparseTextEmbedding("Qdrant/bm25")



app = Flask(__name__)

S3_BASE = "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com"
CLOUDFRONT_BASE = "https://d1zgby2rss028i.cloudfront.net"

# Folder for demo images
IMAGE_FOLDER = os.path.join("static", "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

with open("url_fps_mapping.json") as f:
    url_fps_mapping = json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/db")
def list_db():
    images = os.listdir(IMAGE_FOLDER)
    return jsonify({"images": images})

@app.route("/image/<filename>")
def get_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route("/upload", methods=["POST"])
def upload_images():
    files = request.files.getlist("images")
    for file in files:
        file.save(os.path.join(IMAGE_FOLDER, file.filename))
    return jsonify({"status": "ok"})

@app.route("/query", methods=["POST"])
def query_image():
    data = request.get_json()
    query = data.get("query", "")
    flag = data.get("flag", False)
    flagValue = data.get("flagValue", "")
    image_results = image_search(query, clip_embedding, image_qdrant_client)
    if flagValue is not None:
        content_results = content_search(query, bgem3_embedding, bm25_embedding, content_qdrant_client)

        # Rerank the image results
        reranked_results = rerank_images(image_results, content_results)

        # Prepare the final results for JSON response, take top 20
        final_results = [f"{CLOUDFRONT_BASE}/{res['path']}" for res in reranked_results]

        return jsonify({"images": final_results[:200]})
    else:
        return jsonify({"images": [f"{CLOUDFRONT_BASE}/{res['path']}" for res in image_results[:200]]})
    
    # Mock list (CloudFront)
    # mock_keys = [
    #     "Keyframes_L30_a/L30_V001/000000.webp",
    #     "Keyframes_L30_a/L30_V001/000037.webp",
    #     "Keyframes_L30_a/L30_V001/000074.webp",
    #     "Keyframes_L30_a/L30_V001/000075.webp",
    #     "Keyframes_L30_a/L30_V001/000122.webp",
    #     "Keyframes_L30_a/L30_V001/000169.webp",
    #     "Keyframes_L30_a/L30_V001/000170.webp",
    #     "Keyframes_L30_a/L30_V001/000229.webp",
    #     "Keyframes_L30_a/L30_V001/000289.webp",
    #     "Keyframes_L30_a/L30_V001/000290.webp",
    #     "Keyframes_L30_a/L30_V001/000310.webp",
    #     "Keyframes_L30_a/L30_V001/000330.webp",
    #     "Keyframes_L30_a/L30_V001/000331.webp",
    #     "Keyframes_L30_a/L30_V001/000342.webp",
    #     "Keyframes_L30_a/L30_V001/000353.webp",
    #     "Keyframes_L30_a/L30_V001/000354.webp",
    #     "Keyframes_L30_a/L30_V001/000359.webp",
    #     "Keyframes_L30_a/L30_V001/000365.webp",
    #     "Keyframes_L30_a/L30_V001/000366.webp",
    #     "Keyframes_L30_a/L30_V001/000373.webp",
    #     "Keyframes_L30_a/L30_V001/000380.webp",
    #     "Keyframes_L30_a/L30_V001/000381.webp",
    #     "Keyframes_L30_a/L30_V001/000388.webp",
    #     "Keyframes_L30_a/L30_V001/000396.webp",
    #     "Keyframes_L30_a/L30_V001/000397.webp",
    #     "Keyframes_L30_a/L30_V001/000404.webp",
    #     "Keyframes_L30_a/L30_V001/000412.webp",
    #     "Keyframes_L30_a/L30_V001/000413.webp",
    #     "Keyframes_L30_a/L30_V001/000435.webp",
    #     "Keyframes_L30_a/L30_V001/000457.webp",
    #     "Keyframes_L30_a/L30_V001/000458.webp",
    #     "Keyframes_L30_a/L30_V001/000492.webp",
    #     "Keyframes_L30_a/L30_V001/000527.webp",
    #     "Keyframes_L30_a/L30_V001/000528.webp",
    #     "Keyframes_L30_a/L30_V001/000568.webp",
    #     "Keyframes_L30_a/L30_V001/000608.webp",
    #     "Keyframes_L30_a/L30_V001/000609.webp",
    #     "Keyframes_L30_a/L30_V001/000631.webp",
    #     "Keyframes_L30_a/L30_V001/000654.webp",
    #     "Keyframes_L30_a/L30_V001/000655.webp",
    #     "Keyframes_L30_a/L30_V001/000702.webp",
    #     "Keyframes_L30_a/L30_V001/000749.webp",
    #     "Keyframes_L30_a/L30_V001/000750.webp",
    #     "Keyframes_L30_a/L30_V001/000784.webp",
    #     "Keyframes_L30_a/L30_V001/000819.webp",
    #     "Keyframes_L30_a/L30_V001/000820.webp",
    #     "Keyframes_L30_a/L30_V001/000841.webp",
    #     "Keyframes_L30_a/L30_V001/000862.webp",
    #     "Keyframes_L30_a/L30_V001/000863.webp",
    #     "Keyframes_L30_a/L30_V001/000891.webp",
    #     "Keyframes_L30_a/L30_V001/000919.webp",
    #     "Keyframes_L30_a/L30_V001/000920.webp",
    #     "Keyframes_L30_a/L30_V001/000992.webp",
    #     "Keyframes_L30_a/L30_V001/001064.webp",
    #     "Keyframes_L30_a/L30_V001/001066.webp",
    #     "Keyframes_L30_a/L30_V001/001091.webp",
    #     "Keyframes_L30_a/L30_V001/001116.webp",
    #     "Keyframes_L30_a/L30_V001/001117.webp",
    #     "Keyframes_L30_a/L30_V001/001148.webp",
    #     "Keyframes_L30_a/L30_V001/001180.webp",
    #     "Keyframes_L30_a/L30_V001/001181.webp",
    #     "Keyframes_L30_a/L30_V001/001201.webp",
    #     "Keyframes_L30_a/L30_V001/001221.webp",
    #     "Keyframes_L30_a/L30_V001/001222.webp",
    #     "Keyframes_L30_a/L30_V001/001240.webp",
    #     "Keyframes_L30_a/L30_V001/001258.webp",
    #     "Keyframes_L30_a/L30_V001/001259.webp",
    #     "Keyframes_L30_a/L30_V001/001284.webp",
    #     "Keyframes_L30_a/L30_V001/001310.webp",
    #     "Keyframes_L30_a/L30_V001/001311.webp",
    #     "Keyframes_L30_a/L30_V001/001345.webp",
    #     "Keyframes_L30_a/L30_V001/001380.webp",
    #     "Keyframes_L30_a/L30_V001/001381.webp",
    #     "Keyframes_L30_a/L30_V001/001407.webp",
    #     "Keyframes_L30_a/L30_V001/001434.webp",
    #     "Keyframes_L30_a/L30_V001/001435.webp",
    #     "Keyframes_L30_a/L30_V001/001462.webp",
    #     "Keyframes_L30_a/L30_V001/001490.webp",
    #     "Keyframes_L30_a/L30_V001/001491.webp",
    #     "Keyframes_L30_a/L30_V001/001517.webp",
    #     "Keyframes_L30_a/L30_V001/001544.webp",
    #     "Keyframes_L30_a/L30_V001/001545.webp",
    #     "Keyframes_L30_a/L30_V001/001573.webp",
    #     "Keyframes_L30_a/L30_V001/001602.webp",
    #     "Keyframes_L30_a/L30_V001/001603.webp",
    #     "Keyframes_L30_a/L30_V001/001626.webp",
    #     "Keyframes_L30_a/L30_V001/001649.webp",
    #     "Keyframes_L30_a/L30_V001/001650.webp",
    #     "Keyframes_L30_a/L30_V001/001708.webp",
    #     "Keyframes_L30_a/L30_V001/001767.webp",
    #     "Keyframes_L30_a/L30_V001/001768.webp",
    #     "Keyframes_L30_a/L30_V001/001789.webp",
    #     "Keyframes_L30_a/L30_V001/001810.webp",
    #     "Keyframes_L30_a/L30_V001/001811.webp",
    #     "Keyframes_L30_a/L30_V001/001834.webp",
    #     "Keyframes_L30_a/L30_V001/001857.webp",
    #     "Keyframes_L30_a/L30_V001/001858.webp",
    #     "Keyframes_L30_a/L30_V001/001885.webp",
    #     "Keyframes_L30_a/L30_V001/001912.webp",
    #     "Keyframes_L30_a/L30_V001/001913.webp",
    #     "Keyframes_L30_a/L30_V001/001952.webp",
    #     "Keyframes_L30_a/L30_V001/001992.webp",
    #     "Keyframes_L30_a/L30_V001/001993.webp",
    #     "Keyframes_L30_a/L30_V001/002015.webp",
    #     "Keyframes_L30_a/L30_V001/002037.webp",
    #     "Keyframes_L30_a/L30_V001/002038.webp",
    #     "Keyframes_L30_a/L30_V001/002069.webp",
    #     "Keyframes_L30_a/L30_V001/002100.webp",
    #     "Keyframes_L30_a/L30_V001/002101.webp",
    #     "Keyframes_L30_a/L30_V001/002123.webp",
    #     "Keyframes_L30_a/L30_V001/002146.webp",
    #     "Keyframes_L30_a/L30_V001/002147.webp",
    #     "Keyframes_L30_a/L30_V001/002173.webp",
    #     "Keyframes_L30_a/L30_V001/002199.webp",
    #     "Keyframes_L30_a/L30_V001/002200.webp",
    #     "Keyframes_L30_a/L30_V001/002216.webp",
    #     "Keyframes_L30_a/L30_V001/002232.webp",
    #     "Keyframes_L30_a/L30_V001/002233.webp",
    #     "Keyframes_L30_a/L30_V001/002255.webp",
    #     "Keyframes_L30_a/L30_V001/002278.webp",
    #     "Keyframes_L30_a/L30_V001/002279.webp",
    #     "Keyframes_L30_a/L30_V001/002301.webp",
    #     "Keyframes_L30_a/L30_V001/002324.webp",
    #     "Keyframes_L30_a/L30_V001/002325.webp",
    #     "Keyframes_L30_a/L30_V001/002343.webp",
    #     "Keyframes_L30_a/L30_V001/002362.webp",
    #     "Keyframes_L30_a/L30_V001/002364.webp",
    #     "Keyframes_L30_a/L30_V001/002388.webp",
    #     "Keyframes_L30_a/L30_V001/002412.webp",
    #     "Keyframes_L30_a/L30_V001/002413.webp",
    #     "Keyframes_L30_a/L30_V001/002438.webp",
    #     "Keyframes_L30_a/L30_V001/002464.webp",
    #     "Keyframes_L30_a/L30_V001/002465.webp",
    #     "Keyframes_L30_a/L30_V001/002499.webp",
    #     "Keyframes_L30_a/L30_V001/002534.webp",
    #     "Keyframes_L30_a/L30_V001/002535.webp",
    #     "Keyframes_L30_a/L30_V001/002567.webp",
    #     "Keyframes_L30_a/L30_V001/002600.webp",
    #     "Keyframes_L30_a/L30_V001/002601.webp",
    #     "Keyframes_L30_a/L30_V001/002636.webp",
    #     "Keyframes_L30_a/L30_V001/002672.webp",
    #     "Keyframes_L30_a/L30_V001/002673.webp",
    #     "Keyframes_L30_a/L30_V001/002693.webp",
    #     "Keyframes_L30_a/L30_V001/002713.webp",
    #     "Keyframes_L30_a/L30_V001/002714.webp",
    #     "Keyframes_L30_a/L30_V001/002782.webp",
    #     "Keyframes_L30_a/L30_V001/002851.webp",
    #     "Keyframes_L30_a/L30_V001/002852.webp",
    #     "Keyframes_L30_a/L30_V001/002891.webp",
    #     "Keyframes_L30_a/L30_V001/002931.webp",
    #     "Keyframes_L30_a/L30_V001/002932.webp",
    #     "Keyframes_L30_a/L30_V001/002959.webp",
    #     "Keyframes_L30_a/L30_V001/002987.webp",
    #     "Keyframes_L30_a/L30_V001/002989.webp",
    #     "Keyframes_L30_a/L30_V001/003075.webp",
    #     "Keyframes_L30_a/L30_V001/003161.webp",
    # ]

    # mock_results = [f"{CLOUDFRONT_BASE}/{key}" for key in mock_keys]
    # return jsonify({"images": mock_results})

@app.route("/frames", methods=["GET"])
def get_frames():
    url = request.args.get("url")
    before = int(request.args.get("prev", 25))
    after = int(request.args.get("next", 25))

    if not url:
        return jsonify({"error": "url is required"}), 400

    # Nếu client gửi full url -> chỉ lấy phần key
    if url.startswith("http"):
        key = url.replace(CLOUDFRONT_BASE + "/", "")
    else:
        key = url

    try:
        neighbors = get_neighbor_frames(key, before=before, after=after)
        # build full URL cho frontend
        neighbors_full = [f"{CLOUDFRONT_BASE}/{n}" for n in neighbors]
        return jsonify({"frames": neighbors_full})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/url_fps_mapping.json")
def get_video_mapping():
    return send_from_directory(".", "url_fps_mapping.json")


if __name__ == "__main__":
    app.run(debug=True)
