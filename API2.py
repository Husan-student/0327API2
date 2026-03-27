from flask import Flask, render_template, redirect, url_for, jsonify
import requests
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)


# --- Step 2: 資料庫初始化 (依據 PDF Schema 規範) --- [cite: 31, 32, 33]
def init_db():
    if not os.path.exists("Database"):
        os.makedirs("Database")
    conn = sqlite3.connect("Database/test.db")
    cursor = conn.cursor()
    # 建立符合規範的資料表：id, source, title, content [cite: 33]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            content TEXT,
            created_at DATETIME
        )
    """)
    conn.commit()
    conn.close()


# --- 按鈕 A: 取得天氣 API 資料並寫入 SQLite --- [cite: 12, 22]
@app.route("/fetch_weather")
def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=25.0478&longitude=121.5319&current=temperature_2m,wind_speed_10m,precipitation_probability&timezone=Asia%2FTaipei"
    try:
        data = requests.get(url).json()
        temp = data["current"]["temperature_2m"]
        wind = data["current"]["wind_speed_10m"]
        rain = data["current"]["precipitation_probability"]

        # 整理成 content 字串存入
        weather_info = f"溫度: {temp}°C, 風速: {wind} km/h, 降雨: {rain}%"

        conn = sqlite3.connect("Database/test.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO external_data (source, title, content, created_at)
            VALUES (?, ?, ?, ?)
        """,
            (
                "Open-Meteo",
                "台北即時天氣",
                weather_info,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("view_data"))
    except Exception as e:
        return f"抓取失敗: {e}"


# --- 按鈕 B: 從 GitHub 取得資料 (範例) --- [cite: 13, 20]
@app.route("/fetch_github")
def fetch_github():
    # 範例：抓取自己的 GitHub 資訊或指定專案
    url = "https://api.github.com/repos/python/cpython"
    data = requests.get(url).json()

    conn = sqlite3.connect("Database/test.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO external_data (source, title, content, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (
            "GitHub",
            data["full_name"],
            f"Stars: {data['stargazers_count']}, Language: {data['language']}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("view_data"))


# --- 按鈕 C: 查看已存資料 (資料視覺化頁面) --- [cite: 14]
@app.route("/view")
def view_data():
    conn = sqlite3.connect("Database/test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM external_data ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return render_template("view.html", data=rows)


# --- 跨機 API 互動: 提供自己的資料給同學抓取 --- [cite: 50, 52]
@app.route("/api/data")
def api_provide():
    conn = sqlite3.connect("Database/test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM external_data")
    rows = cursor.fetchall()
    conn.close()
    # 轉換成 JSON 格式
    return jsonify([{"source": r[1], "title": r[2], "content": r[3]} for r in rows])


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    # 設定 0.0.0.0 讓同學能連進來 [cite: 52]
    app.run(host="0.0.0.0", port=5000, debug=True)
