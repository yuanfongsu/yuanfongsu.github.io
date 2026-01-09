from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 1. 首頁測試路由 (確認伺服器是否活著)
@app.route('/')
def home():
    return "<h1>Python Server is Running! (伺服器運作中)</h1><p>請回到網頁點擊掃描。</p>"

# 2. 代理路由
@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return Response("Error: Missing URL parameter", status=400)
    
    print(f"正在嘗試抓取: {url}") # 在黑色視窗印出正在抓什麼
    
    try:
        # 偽裝成瀏覽器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 設定 verify=False 忽略 SSL 憑證問題
        resp = requests.get(url, headers=headers, stream=True, timeout=10, verify=False)
        
        # 如果對方伺服器回傳錯誤 (例如 404 或 403)
        if resp.status_code != 200:
            print(f"抓取失敗，狀態碼: {resp.status_code}")
            return Response(f"Remote Error: {resp.status_code}", status=resp.status_code)

        # 複製必要的 headers 回傳
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        print("抓取成功！正在回傳給網頁...")
        return Response(resp.content, resp.status_code, headers)

    except Exception as e:
        print(f"發生錯誤: {e}")
        return Response(f"Server Error: {str(e)}", status=500)

if __name__ == '__main__':
    print("🚀 Proxy Server running on http://localhost:5000")
    print("請不要關閉此視窗...")
    
    # 關閉 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    app.run(port=5000, debug=True)
