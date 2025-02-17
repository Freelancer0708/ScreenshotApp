from flask import Flask, render_template, request, Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import os
import tempfile

app = Flask(__name__)

# 環境変数からベーシック認証のユーザー名とパスワードを取得
BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD")

# スクリーンショットを保存するディレクトリ
os.makedirs("static/screenshots", exist_ok=True)

def take_screenshot(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 一意のディレクトリを作成して指定する
    temp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_user_data_dir}")
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    screenshot_path = "static/screenshots/screenshot.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()
    return screenshot_path

def fetch_html_structure(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.prettify()

# ベーシック認証を実装
def check_auth(username, password):
    """ 環境変数と一致するかを確認 """
    return username == BASIC_AUTH_USERNAME and password == BASIC_AUTH_PASSWORD

def authenticate():
    """ 認証失敗時のレスポンス """
    return Response(
        "認証が必要です。ブラウザでユーザー名とパスワードを入力してください。",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    if request.method == 'POST':
        url = request.form['url']
        screenshot_path = take_screenshot(url)
        html_structure = fetch_html_structure(url)
        return render_template('index.html', screenshot=screenshot_path, html_structure=html_structure, url=url)
    
    return render_template('index.html', screenshot=None, html_structure=None)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
