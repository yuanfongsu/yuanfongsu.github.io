import cv2
import numpy as np
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "<h1>CCTV Snapshot Server is Running!</h1>"

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return Response("Error: Missing URL", status=400)
    
    print(f"正在擷取影像: {url}")
    
    try:
        # 使用 OpenCV 連接影片串流
        cap = cv2.VideoCapture(url)
        
        # 嘗試讀取一個畫面 (Frame)
        success, frame = cap.read()
        
        # 記得釋放連線，不然測站會被佔用
        cap.release()
        
        if not success:
            print("讀取失敗：無法取得畫面")
            return Response("Failed to grab frame", status=500)

        # 將畫面編碼為 JPEG 格式
        # quality 設定為 80 可以稍微壓縮，加快傳輸速度
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        if not ret:
            print("編碼失敗")
            return Response("Failed to encode image", status=500)

        # 回傳靜態圖片給網頁
        print("截圖成功！")
        return Response(buffer.tobytes(), mimetype='image/jpeg')

    except Exception as e:
        print(f"發生錯誤: {e}")
        return Response(str(e), status=500)

if __name__ == '__main__':
    print("🚀 Snapshot Server running on http://localhost:5000")
    # 因為 OpenCV 本身處理了網路層，這裡不需要 urllib3 的警告設定
    app.run(port=5000, debug=True)
