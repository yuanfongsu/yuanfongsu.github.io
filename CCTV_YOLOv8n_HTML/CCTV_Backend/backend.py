import os
import cv2
import numpy as np
import base64
import time
import requests
import urllib3
import re
from urllib.parse import urljoin
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# ================= 設定區 =================
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;3000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
CSV_PATH = os.path.join(BASE_DIR, "cctv_with_counties_final.csv")

print("--------------------------------------------------")
print(f"🔄 正在載入 YOLO 模型: {MODEL_PATH} ...")
try:
    model = YOLO(MODEL_PATH)
    print("✅ 模型載入成功！")
except Exception as e:
    print(f"❌ 模型載入失敗: {e}")
    model = None
print("--------------------------------------------------")

# ================= HTML 解析與影像抓取 =================

def extract_image_url_from_html(html_content, base_url):
    try:
        html_text = html_content.decode('utf-8', errors='ignore')
        patterns = [
            r'<img[^>]+src=["\']([^"\']*(?:GetImage|Snapshot|Stream)[^"\']*)["\']',
            r'<img[^>]+id=["\']imgCCTV["\'][^>]+src=["\']([^"\']+)["\']',
            r'<img[^>]+src=["\']([^"\']+)["\']'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, html_text, re.IGNORECASE)
            for match in matches:
                if any(x in match.lower() for x in ['.gif', 'logo', 'icon', 'button', 'banner']): continue
                return urljoin(base_url, match)
    except Exception as e:
        print(f"⚠️ HTML 解析失敗: {e}")
    return None

def grab_mjpeg_frame(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://motoretag.taichung.gov.tw/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }
        with requests.get(url, stream=True, timeout=6, headers=headers, verify=False) as r:
            if r.status_code != 200: return None
            
            content_type = r.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                real_image_url = extract_image_url_from_html(r.content, url)
                if real_image_url and real_image_url != url:
                    return grab_mjpeg_frame(real_image_url)
                return None

            bytes_data = bytes()
            for chunk in r.iter_content(chunk_size=4096):
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    return cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
    except:
        pass
    return None

def grab_image(url):
    if "http" in url and ("taichung" in url or "Showcctv" in url or "mjpeg" in url.lower()):
        frame = grab_mjpeg_frame(url)
        if frame is not None: return frame
    try:
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)
        if not cap.isOpened(): return None
        success, frame = cap.read()
        cap.release()
        return frame if success else None
    except:
        return None

def draw_flood_edges(frame, results):
    img = frame.copy()
    if results[0].masks is not None:
        for mask_contour in results[0].masks.xy:
            if len(mask_contour) > 0:
                points = np.int32([mask_contour])
                cv2.polylines(img, points, isClosed=True, color=(0, 0, 255), thickness=2)
    return img

# ================= API 路由 =================

@app.route('/get_csv', methods=['GET'])
def get_csv():
    if os.path.exists(CSV_PATH):
        return send_file(CSV_PATH, mimetype='text/csv')
    return jsonify({"status": "error", "message": "CSV not found"}), 404

@app.route('/detect', methods=['GET'])
def detect_flood():
    if model is None: return jsonify({"status": "error", "message": "Model not loaded"}), 500
    
    url = request.args.get('url')
    if not url: return jsonify({"status": "error", "message": "No URL"}), 400

    # 【修改點】讀取前端傳來的信心度參數 (conf)，預設為 0.25 (後端保底)
    try:
        conf_threshold = float(request.args.get('conf', 0.25))
    except ValueError:
        conf_threshold = 0.25

    frame = grab_image(url)
    if frame is None:
        return jsonify({"status": "error", "message": "Camera Offline"}), 503

    # 【修改點】將 conf_threshold 傳入 YOLO
    results = model.predict(frame, conf=conf_threshold, classes=[0], retina_masks=True, verbose=False)
    
    is_flooded = False
    confidence = 0.0
    frame_labeled = frame

    if len(results) > 0:
        if results[0].masks is not None:
            is_flooded = True
            if len(results[0].boxes.conf) > 0:
                confidence = float(results[0].boxes.conf[0])
            frame_labeled = draw_flood_edges(frame, results)

    _, buffer = cv2.imencode('.jpg', frame_labeled, [cv2.IMWRITE_JPEG_QUALITY, 70])
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        "status": "success",
        "is_flooded": is_flooded,
        "confidence": round(confidence, 2),
        "image_base64": f"data:image/jpeg;base64,{img_b64}"
    })

if __name__ == '__main__':
    print("🚀 Backend Updated (Dynamic Confidence) 已啟動 (Port 5000)")
    app.run(port=5000, debug=False, threaded=True)