import os
import cv2
import numpy as np
import base64
import time
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ================= 設定區 =================
# 1. 設定 FFmpeg 參數：強制將連線逾時設定為 5000ms (5秒)，避免卡住 30秒
# 注意：這行必須在 cv2.VideoCapture 之前設定
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;5000"

TARGET_PATH = r"G:\我的雲端硬碟\Flood_Alerts"

# 2. 自動檢查與建立資料夾
if os.path.exists(r"G:\我的雲端硬碟"):
    GOOGLE_DRIVE_PATH = TARGET_PATH
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    GOOGLE_DRIVE_PATH = os.path.join(BASE_DIR, "Flood_Alerts")
    print(f"⚠️ 偵測不到 G 槽，改為存檔至本機目錄: {GOOGLE_DRIVE_PATH}")

if not os.path.exists(GOOGLE_DRIVE_PATH):
    try:
        os.makedirs(GOOGLE_DRIVE_PATH)
        print(f"✅ 已建立資料夾: {GOOGLE_DRIVE_PATH}")
    except Exception as e:
        print(f"❌ 無法建立資料夾: {e}")

# ================= 1. 圖片代理 (Proxy - 高速版) =================
@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return Response("Error: Missing URL", status=400)
    
    max_retries = 2  # 減少重試次數，加快掃描速度
    
    for attempt in range(max_retries):
        cap = None
        try:
            # 使用 API_PREFERENCE 強制指定後端，有助於 Windows 穩定性
            # CAP_ANY 是自動選擇，通常沒問題
            cap = cv2.VideoCapture(url, cv2.CAP_ANY)
            
            # 設定 3 秒逾時 (部分 OpenCV 版本支援此參數)
            # 如果不支援，上面的 os.environ 會起作用
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)

            if not cap.isOpened():
                time.sleep(0.5)
                continue

            success, frame = cap.read()
            cap.release()
            
            if not success:
                time.sleep(0.5)
                continue

            # 編碼
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            if ret:
                return Response(buffer.tobytes(), mimetype='image/jpeg')
            else:
                time.sleep(0.5)

        except Exception as e:
            # print(f"⚠️ [{attempt+1}] 異常: {e}") # 隱藏詳細錯誤讓畫面乾淨點
            if cap and cap.isOpened():
                cap.release()
            time.sleep(0.5)

    # 失敗時回傳 500，但不印出大量錯誤訊息干擾視線
    return Response("Timeout", status=500)

# ================= 2. 儲存警報圖片 =================
@app.route('/save_alert', methods=['POST'])
def save_alert():
    try:
        data = request.json
        cctv_name = data.get('name', 'Unknown')
        img_original_b64 = data.get('image_original')
        img_labeled_b64 = data.get('image_labeled')
        
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

        print(f"💾 已存檔: {safe_name}")
        return jsonify({"status": "success", "path": GOOGLE_DRIVE_PATH})

    except Exception as e:
        print(f"❌ 存檔失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def save_base64_image(b64_string, file_path):
    if ',' in b64_string:
        b64_string = b64_string.split(',')[1]
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(b64_string))

if __name__ == '__main__':
    print("==================================================")
    print("🚀 CCTV Backend (高速逾時版) 已啟動")
    print(f"📂 存檔路徑: {GOOGLE_DRIVE_PATH}")
    print("==================================================")
    # threaded=True 允許同時處理多個請求，避免一個卡住全部卡住
    app.run(port=5000, debug=True, threaded=True)
