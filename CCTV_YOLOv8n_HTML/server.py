from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # 允許所有跨域請求

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return Response("Missing URL", status=400)
    
    try:
        # Python 偽裝成瀏覽器去抓圖，避開防火牆阻擋
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, stream=True, timeout=10, verify=False)
        
        # 將抓到的圖片直接轉傳回去
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return Response(str(e), status=500)

if __name__ == '__main__':
    print("🚀 Proxy Server running on http://localhost:5000")
    # SSL 驗證關閉警告消除
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app.run(port=5000, debug=True)
