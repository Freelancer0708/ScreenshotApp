from flask import Flask, request, render_template, Response, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import time
from dotenv import load_dotenv
from functools import wraps

# 環境変数をロード
load_dotenv()

# staticフォルダがなければ作成
if not os.path.exists("static"):
    os.makedirs("static")

app = Flask(__name__)

# Basic Authentication
USERNAME = os.getenv("ADMIN_USER")
PASSWORD = os.getenv("ADMIN_PASS")

if not USERNAME or not PASSWORD:
    raise ValueError("環境変数 ADMIN_USER と ADMIN_PASS を設定してください")

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        "Could not verify your access level for that URL.", 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET', 'POST'])
@requires_auth
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return render_template('index.html', error='URLを入力してください')
        
        try:
            # Set up Selenium headless browser
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--remote-debugging-port=9222')

            driver = webdriver.Chrome(options=chrome_options)
            
            driver.get(url)
            driver.implicitly_wait(10)  # 10秒待機
            
            timestamp = int(time.time())
            screenshot_path = f"static/screenshot_{timestamp}.png"
            driver.save_screenshot(screenshot_path)
            
            # Get page source
            html_source = driver.page_source
            driver.quit()
            
            soup = BeautifulSoup(html_source, 'html.parser')
            formatted_html = soup.prettify()
            
            return render_template('index.html', screenshot=screenshot_path, html_code=formatted_html, url=url)
        except Exception as e:
            return render_template('index.html', error=f'エラー: {str(e)}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
