import requests

# 這裡填入你同學的 IP 位址 [cite: 50]
TARGET_IP = "10.22.234.177"  # 練習時可先用自己連自己

try:
    response = requests.get(f"http://{TARGET_IP}:5000/api/data")
    if response.status_code == 200:
        data = response.json()
        print(f"成功！共取得 {len(data)} 筆資料")
        for idx, item in enumerate(data, 1):
            print(f"[{idx}] 來源: {item['source']} | 標題: {item['title']}")
    else:
        print("連線失敗")
except Exception as e:
    print(f"錯誤: {e}")
