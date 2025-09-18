from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import json
from sympy import limit
from s3.s3_utils import get_neighbor_frames  # import hàm có sẵn
from src.search.search_service import CombinedSearchService,CaptionSearchService,ImageSearchService



app = Flask(__name__)
search_service =ImageSearchService(max_workers=64) # only image search
# search_service = CaptionSearchService(max_workers=64) # only caption search
# search_service = CombinedSearchService(max_workers = 64) # combine 2 methods search

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
    
    return await search_service.process_with_executor(request)


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
