FROM n8nio/n8n:latest

# 安裝Python和必要的依賴
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    gnupg \
    unzip \
    xvfb \
    libgbm1 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm-dev \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 安裝Chrome瀏覽器
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 安裝Python依賴
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# 創建目錄結構
RUN mkdir -p /app/scripts /tmp/downloads

# 複製腳本和工作流文件
COPY scripts/* /app/scripts/
COPY n8n_workflow.json /app/

# 設置執行權限
RUN chmod +x /app/scripts/*.py

# 安裝工作流
WORKDIR /data/.n8n
RUN mkdir -p /data/.n8n/workflows
RUN cp /app/n8n_workflow.json /data/.n8n/workflows/workflow.json

# 切換回n8n用戶
USER node

# 設置環境變量
ENV EXECUTIONS_PROCESS=main
ENV GENERIC_TIMEZONE="Asia/Taipei"
ENV TZ="Asia/Taipei"

# 啟動n8n
CMD ["n8n", "start"] 