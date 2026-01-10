import os
import cv2  # 這是關鍵：回復使用 OpenCV
import numpy as np
import base64
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ================= 設定區 =================
# 請確認您的 Google Drive 路徑
GOOGLE_DRIVE_PATH = r"G:\我的雲端硬碟\Flood_Alerts"

# 如果資料夾不存在，自動建立
if not os.path.exists(GOOGLE_DRIVE_PATH):
    try:
        os.makedirs(GOOGLE_DRIVE_PATH)
        print(f"✅ 已建立資料夾: {GOOGLE_DRIVE_PATH}")
    except Exception as e:
        print(f"❌ 無法建立資料夾 (請確認 G 槽是否已連線): {e}")
        # 如果 G 槽真的讀不到，自動切換回本機資料夾
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        GOOGLE_DRIVE_PATH = os.path.join(BASE_DIR, "Flood_Alerts")
        print(f"⚠️ 改為存檔至程式所在目錄: {GOOGLE_DRIVE_PATH}")
        if not os.path.exists(GOOGLE_DRIVE_PATH):
            os.makedirs(GOOGLE_DRIVE_PATH)

# ================= 1. 圖片代理 (Proxy - 改回 OpenCV) =================
@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return Response("Error: Missing URL", status=400)
    
    # print(f"正在擷取影像: {url}") # 除錯用，若訊息太多可註解掉
    
    try:
        # 【關鍵修改】使用 OpenCV 連接影片串流 (回復 server.py 的邏輯)
        cap = cv2.VideoCapture(url)
        
        if not cap.isOpened():
            return Response("Failed to open stream", status=500)

        # 嘗試讀取一個畫面 (Frame)
        success, frame = cap.read()
        cap.release() # 釋放連線
        
        if not success:
            return Response("Failed to grab frame", status=500)

        # 將畫面編碼為 JPEG 格式
        # quality 設定為 80 加快傳輸
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        if not ret:
            return Response("Failed to encode image", status=500)

        # 回傳靜態圖片給網頁
        return Response(buffer.tobytes(), mimetype='image/jpeg')

    except Exception as e:
        print(f"擷取錯誤: {e}")
        return Response(str(e), status=500)

# ================= 2. 儲存警報圖片 (Save Alert) =================
@app.route('/save_alert', methods=['POST'])
def save_alert():
    try:
        data = request.json
        cctv_name = data.get('name', 'Unknown')
        img_original_b64 = data.get('image_original')
        img_labeled_b64 = data.get('image_labeled')
        
        # 產生時間戳記檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join([c for c in cctv_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        
        filename_orig = f"{timestamp}_{safe_name}_ORIG.jpg"
        filename_lbl = f"{timestamp}_{safe_name}_ALERT.jpg"
        
        path_orig = os.path.join(GOOGLE_DRIVE_PATH, filename_orig)
        path_lbl = os.path.join(GOOGLE_DRIVE_PATH, filename_lbl)

        if img_original_b64:
            save_base64_image(img_original_b64, path_orig)
        
        if img_labeled_b64:
            save_base64_image(img_labeled_b64, path_lbl)

        print(f"✅ 已儲存警報: {cctv_name} -> {GOOGLE_DRIVE_PATH}")
        return jsonify({"status": "success", "path": GOOGLE_DRIVE_PATH})

    except Exception as e:
        print(f"❌ 儲存失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def save_base64_image(b64_string, file_path):
    if ',' in b64_string:
        b64_string = b64_string.split(',')[1]
    
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(b64_string))

if __name__ == '__main__':
    print("🚀 Snapshot Server (OpenCV + Google Drive) running on http://localhost:5000")
    print(f"📂 存檔路徑: {GOOGLE_DRIVE_PATH}")
    app.run(port=5000, debug=True)