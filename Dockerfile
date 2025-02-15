# ベースイメージ
FROM python:3.9

# 作業ディレクトリ
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリのソースコードをコピー
COPY . .

# ポートの公開
EXPOSE 5000

# アプリの起動
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
