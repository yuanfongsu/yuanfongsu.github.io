import pandas as pd
import os

# 設定檔案名稱 (請確認這些檔案都在同一個資料夾)
MAIN_CSV = 'cctv_with_counties.csv'
TAICHUNG_CSV = '臺中市交通影像靜態資訊.csv'
OUTPUT_CSV = 'cctv_with_counties_updated.csv'

def merge_cctv_data():
    # 1. 檢查檔案是否存在
    if not os.path.exists(MAIN_CSV) or not os.path.exists(TAICHUNG_CSV):
        print(f"❌ 找不到檔案！請確認 {MAIN_CSV} 和 {TAICHUNG_CSV} 都在資料夾內。")
        return

    print("📖 正在讀取檔案...")
    df_main = pd.read_csv(MAIN_CSV)
    df_tc = pd.read_csv(TAICHUNG_CSV)

    # 2. 處理臺中市資料
    print("🔄 正在轉換臺中市資料格式...")
    df_tc_new = df_tc.copy()

    # 對應欄位
    df_tc_new['VideoImageURL'] = df_tc_new['url']
    df_tc_new['經度'] = df_tc_new['px']
    df_tc_new['緯度'] = df_tc_new['py']
    df_tc_new['CCTVID'] = df_tc_new['cctvid']

    # 處理路名與描述
    def process_road_info(val):
        if not isinstance(val, str): return "", ""
        chinese_part = val.split(',')[0] # 取逗號前的中文
        description = chinese_part
        road_name = chinese_part.split('/')[0].split('(')[0].strip() # 簡單取路名
        return road_name, description

    df_tc_new[['道路名稱', '位置描述']] = df_tc_new['roadsection'].apply(
        lambda x: pd.Series(process_road_info(x))
    )

    # 補上縣市資訊
    df_tc_new['COUNTYNAME'] = '臺中市'
    df_tc_new['COUNTYCODE'] = 66000
    df_tc_new['COUNTYID'] = 'B'
    df_tc_new['COUNTYENG'] = 'Taichung City'
    df_tc_new['geometry'] = df_tc_new.apply(lambda row: f"POINT ({row['經度']} {row['緯度']})", axis=1)

    # 3. 欄位對齊 (確保跟主檔案一樣)
    target_columns = df_main.columns.tolist()
    for col in target_columns:
        if col not in df_tc_new.columns:
            df_tc_new[col] = None
    
    df_tc_final = df_tc_new[target_columns]

    # 4. 合併
    print("➕ 正在合併資料...")
    df_combined = pd.concat([df_main, df_tc_final], ignore_index=True)

    # 5. 存檔
    df_combined.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"✅ 成功！已建立新檔案: {OUTPUT_CSV}")
    print(f"   總筆數: {len(df_combined)} (原: {len(df_main)} + 中: {len(df_tc_final)})")

if __name__ == "__main__":
    try:
        merge_cctv_data()
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        # 如果沒有 pandas，提示安裝
        print("💡 提示: 如果出現 'No module named pandas'，請執行: pip install pandas")