# Resmi Python 3.12 imajını kullan
FROM python:3.12-slim

# Gerekli paketleri yükle
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libgl1-mesa-glx \
    libnss3 \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    xdg-utils \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome'un en son versiyonunu indir ve kur
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable

# ChromeDriver'ı indir ve kur
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Python bağımlılıklarını yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Çalışma dizinini oluştur
WORKDIR /app

# Uygulama dosyalarını kopyala
COPY . /app

# 8501 portunu aç
EXPOSE 8501

# Streamlit uygulamasını başlat
CMD ["streamlit", "run", "main.py", "--server.port=8501"]