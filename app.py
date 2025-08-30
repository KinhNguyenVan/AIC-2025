from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import random

from sympy import limit
from s3.s3_utils import get_neighbor_frames 
from src.search.model import clip_embedding, bgem3_embedding, bm25_embedding
from src.search.qdrant_db import image_qdrant_client, content_qdrant_client
from src.search.search import image_search, content_search
from src.rerank.rerank import rerank_images



app = Flask(__name__)

S3_BASE = "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com"

# Folder for demo images
IMAGE_FOLDER = os.path.join("static", "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

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
    image_results = image_search(query, clip_embedding, image_qdrant_client)
    if flag:
        content_results = content_search(query, bgem3_embedding, bm25_embedding, content_qdrant_client)

        # Rerank the image results
        reranked_results = rerank_images(image_results, content_results)

        # Prepare the final results for JSON response, take top 20
        final_results = [f"{S3_BASE}/{res['path']}" for res in reranked_results]

        return jsonify({"images": final_results})
    else:
        return jsonify({"images": [f"{S3_BASE}/{res['path']}" for res in image_results]})

@app.route("/frames", methods=["GET"])
def get_frames():
    url = request.args.get("url")
    before = int(request.args.get("prev", 25))
    after = int(request.args.get("next", 25))

    if not url:
        return jsonify({"error": "url is required"}), 400

    # Nếu client gửi full url -> chỉ lấy phần key
    if url.startswith("http"):
        key = url.replace(S3_BASE + "/", "")
    else:
        key = url

    try:
        neighbors = get_neighbor_frames(key, before=before, after=after)
        # build full URL cho frontend
        neighbors_full = [f"{S3_BASE}/{n}" for n in neighbors]
        return jsonify({"frames": neighbors_full})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
