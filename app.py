from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import random
from s3.s3_utils import get_neighbor_frames  # import hàm có sẵn

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

    # Giả lập output keyframes từ S3
    keyframes = [
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001274.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001299.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001325.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001326.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001359.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001392.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001393.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001428.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001463.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001464.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001499.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001535.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001536.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001574.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001613.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001614.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001647.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001681.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001682.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001720.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001759.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001760.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001787.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001814.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001815.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001839.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001864.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001865.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001886.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001908.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001909.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001935.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001962.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001963.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/001989.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002015.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002016.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002050.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002085.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002086.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002109.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002132.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002133.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002159.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002185.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002186.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002214.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002242.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002243.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002349.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002456.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002457.webp",
        "https://aic-bucket-hcmus.s3.ap-southeast-2.amazonaws.com/Keyframes_L30_a/L30_V064/002596.webp"
    ]

    return jsonify({"images": keyframes})

@app.route("/frames")
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
