import os
import base64
import hashlib
import mimetypes
from datetime import datetime
from io import BytesIO

from flask import Flask, request, jsonify, redirect
from huggingface_hub import HfApi, HfFileSystem
from PIL import Image
import uuid

app = Flask(__name__)

# 环境变量配置
HF_TOKEN = os.environ.get("HF_TOKEN")
DATASET_ID = os.environ.get("DATASET_ID")
MAX_SIZE = int(os.environ.get("MAX_SIZE", 10)) * 1024 * 1024  # 转字节
API_KEY = os.environ.get("API_KEY")

fs = HfFileSystem(token=HF_TOKEN)
hf_api = HfApi(token=HF_TOKEN)

def validate_auth():
    if not API_KEY:
        return True
    header_key = request.headers.get("X-API-Key")
    param_key = request.args.get("key")
    return header_key == API_KEY or param_key == API_KEY

def generate_filename(data, mime_type=None):
    ext = mimetypes.guess_extension(mime_type or "application/octet-stream") or ".bin"
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{unique_id}{ext}"

def save_to_dataset(content, filename):
    path = f"datasets/{DATASET_ID}/resolve/main/images/{filename}"
    fs.mkdir(f"datasets/{DATASET_ID}/images", exist_ok=True)
    fs.write_bytes(f"datasets/{DATASET_ID}/images/{filename}", content)
    return f"https://huggingface.co/datasets/{DATASET_ID}/resolve/main/images/{filename}"

@app.route("/", methods=["GET"])
def index():
    return "HF-PicBed is running..."

@app.route("/api/1/upload", methods=["GET", "POST"])
def upload():
    # 鉴权检查
    if not validate_auth():
        return jsonify({
            "status_code": 401,
            "error": {"message": "Invalid API key"},
            "status_txt": "Unauthorized"
        }), 401

    # 获取文件数据
    source = None
    if request.method == "POST":
        if "source" in request.files:
            file = request.files["source"]
            source = file.read()
        else:
            source = request.form.get("source")
    else:
        source = request.args.get("source")

    # 处理Base64、文件或URL
    if isinstance(source, bytes):
        content = source
    elif source.startswith(("http://", "https://")):
        # 需要实现URL下载逻辑（示例代码省略）
        return jsonify({"error": "URL download not implemented"}), 501
    elif source.startswith("data:"):
        header, data = source.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0]
        content = base64.b64decode(data)
    else:
        content = base64.b64decode(source)

    # 验证大小限制
    if len(content) > MAX_SIZE:
        return jsonify({
            "status_code": 413,
            "error": {"message": f"File exceeds {MAX_SIZE//1024//1024}MB limit"},
            "status_txt": "Payload Too Large"
        }), 413

    # 处理图片属性
    try:
        image = Image.open(BytesIO(content))
        width, height = image.size
        mime_type = image.get_format_mimetype()
    except:
        width = height = 0
        mime_type = None

    # 生成存储信息
    filename = generate_filename(content, mime_type)
    file_url = save_to_dataset(content, filename)

    # 构造响应
    response_format = request.args.get("format", "json")
    if response_format == "txt":
        return file_url
    elif response_format == "redirect":
        return redirect(file_url, code=302)
    else:
        return jsonify({
            "status_code": 200,
            "success": {"message": "file uploaded", "code": 200},
            "image": {
                "filename": filename,
                "url": file_url,
                "size": len(content),
                "width": width,
                "height": height,
                "mime": mime_type,
                "size_formatted": f"{len(content)/1024/1024:.1f} MB"
            },
            "status_txt": "OK"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
