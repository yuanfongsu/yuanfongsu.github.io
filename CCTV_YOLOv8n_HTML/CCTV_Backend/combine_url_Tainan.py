import pandas as pd
import json
import os

# 設定檔案名稱
# 來源 1: 已經包含全台+台中的 CSV
CURRENT_CSV = 'cctv_with_counties_updated.csv'
# 來源 2: 台南市 JSON
TAINAN_JSON = 'cctv_info.json'
# 輸出檔案
OUTPUT_CSV = 'cctv_with_counties_final.csv'

def merge_tainan_data():
    # 1. 檢查檔案
    if not os.path.exists(CURRENT_CSV) or not os.path.exists(TAINAN_JSON):
        print(f"❌ 找不到檔案！請確認 {CURRENT_CSV} 和 {TAINAN_JSON} 都在資料夾內。")
        return

    print("📖 正在讀取現有 CSV 資料...")
    df_main = pd.read_csv(CURRENT_CSV)
    print(f"   目前筆數: {len(df_main)}")

    print("📖 正在讀取臺南市 JSON 資料...")
    with open(TAINAN_JSON, 'r', encoding='utf-8') as f:
        data_tn = json.load(f)
    
    # 轉為 DataFrame
    df_tn = pd.DataFrame(data_tn)

    # 2. 轉換臺南市資料格式
    print("🔄 正在轉換臺南市資料格式...")
    df_tn_new = pd.DataFrame()

    # 對應欄位 (JSON -> CSV)
    df_tn_new['VideoImageURL'] = df_tn['url']
    df_tn_new['經度'] = df_tn['wgsx']
    df_tn_new['緯度'] = df_tn['wgsy']

    # 產生 CCTVID (因為原始資料沒有 ID，我們自動產生 TNN-0001, TNN-0002...)
    df_tn_new['CCTVID'] = [f"TNN-{i:04d}" for i in range(1, len(df_tn) + 1)]

    # 處理路名 (簡單切割)
    def clean_road_name(val):
        if not isinstance(val, str): return ""
        # 取 '與' 或 '路口' 之前的字串作為主要路名
        return val.split('與')[0].split('路口')[0].strip()

    df_tn_new['道路名稱'] = df_tn['Location'].apply(clean_road_name)
    df_tn_new['位置描述'] = df_tn['Location']

    # 補上縣市資訊 (臺南市)
    df_tn_new['COUNTYNAME'] = '臺南市'
    df_tn_new['COUNTYCODE'] = 67000
    df_tn_new['COUNTYID'] = 'D'
    df_tn_new['COUNTYENG'] = 'Tainan City'
    
    # 產生 geometry 欄位
    df_tn_new['geometry'] = df_tn_new.apply(lambda row: f"POINT ({row['經度']} {row['緯度']})", axis=1)

    # 3. 欄位對齊 (確保跟主檔案一樣)
    target_columns = df_main.columns.tolist()
    for col in target_columns:
        if col not in df_tn_new.columns:
            df_tn_new[col] = None
    
    df_tn_final = df_tn_new[target_columns]

    # 4. 合併
    print("➕ 正在合併資料...")
    df_combined = pd.concat([df_main, df_tn_final], ignore_index=True)

    # 5. 存檔
    df_combined.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"✅ 成功！已建立新檔案: {OUTPUT_CSV}")
    print(f"   總筆數: {len(df_combined)} (原: {len(df_main)} + 南: {len(df_tn_final)})")

if __name__ == "__main__":
    try:
        merge_tainan_data()
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")