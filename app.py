from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import os
import tempfile

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        screenshot_path = take_screenshot(url)
        html_structure = fetch_html_structure(url)
        return render_template('index.html', screenshot=screenshot_path, html_structure=html_structure, url=url)
    
    return render_template('index.html', screenshot=None, html_structure=None)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
