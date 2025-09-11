from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import random
import asyncio
import json


from sympy import limit
from s3.s3_utils import get_neighbor_frames  # import hàm có sẵn
from src.search.model import clip_embedding, bgem3_embedding, bm25_embedding, gemini_model
from src.search.qdrant_db import image_qdrant_client_1, content_qdrant_client,image_qdrant_client_2
from src.search.search import image_search_1, content_search, image_search_2
from src.rerank.rerank import rerank_images
from src.utils import deduplicate_and_sort


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
async def query_image():
    data = request.get_json()
    query = data.get("query", "")
    flagValue = data.get("flagValue", "")
    if flagValue is not None and flagValue != "":
        # 3. Nếu flag True thì chạy content search song song
        gemini_task = asyncio.to_thread(gemini_model.generate_content, query)
        content_task = asyncio.to_thread(content_search, flagValue, bgem3_embedding, bm25_embedding, content_qdrant_client)
        eng_query, content_results = await asyncio.gather(
            gemini_task, content_task
        )
        print("Rewritten Query:", eng_query)
        img1_task = asyncio.to_thread(image_search_1, eng_query, clip_embedding, image_qdrant_client_1)
        img2_task = asyncio.to_thread(image_search_2, eng_query, clip_embedding, image_qdrant_client_2)
        image_results_1, image_results_2 = await asyncio.gather(img1_task, img2_task)
        
        # 4. Rerank kết quả
        image_results = image_results_1 + image_results_2
        reranked_results = rerank_images(image_results, content_results)
        final_results = [f"{CLOUDFRONT_BASE}/{res['path']}" for res in reranked_results]
        return jsonify({"images": final_results[:200]})
    else:
        eng_query = gemini_model.generate_content(query)
        print("Rewritten Query:", eng_query)
        img1_task = asyncio.to_thread(image_search_1, eng_query, clip_embedding, image_qdrant_client_1)
        img2_task = asyncio.to_thread(image_search_2, eng_query, clip_embedding, image_qdrant_client_2)
        image_results_1, image_results_2 = await asyncio.gather(img1_task, img2_task)
        image_results = image_results_1 + image_results_2
        image_results = deduplicate_and_sort(image_results, payload_key="path")
        return jsonify({"images": [f"{CLOUDFRONT_BASE}/{res['path']}" for res in image_results[:200]]})
    

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