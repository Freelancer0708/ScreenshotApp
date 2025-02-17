from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def take_screenshot(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # WebDriver Manager を使用して最新の ChromeDriver を取得
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    driver.get(url)
    
    # Render の無料環境では `/tmp/` に保存
    screenshot_path = "/tmp/screenshot.png"
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
        
        # `/screenshot` で画像を提供
        return render_template('index.html', screenshot_url='/screenshot', html_structure=html_structure, url=url)
    
    return render_template('index.html', screenshot_url=None, html_structure=None)

# `/screenshot` エンドポイントを作成し、スクリーンショットを返す
@app.route('/screenshot')
def get_screenshot():
    return send_file("/tmp/screenshot.png", mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
