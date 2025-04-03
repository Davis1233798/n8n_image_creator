# NSFW圖片生成自動發布系統 - 構建指南

本文件詳細說明了如何構建和部署NSFW圖片生成自動發布系統。

## 系統架構

系統採用以下技術構建：

1. **n8n**: 作為工作流自動化引擎
2. **Python**: 用於自動化腳本和API交互
3. **Selenium**: 用於網頁自動化操作
4. **Supabase**: 作為後端數據存儲
5. **Docker**: 用於容器化部署

## 目錄結構

```
/
├── Dockerfile             # Docker容器配置文件
├── docker-compose.yml     # Docker Compose配置
├── requirements.txt       # Python依賴包列表
├── n8n_workflow.json      # n8n工作流定義
├── .env.example           # 環境變量模板文件
└── scripts/               # Python腳本目錄
    ├── generate_images.py        # 圖片生成腳本
    ├── upload_to_nsfw_sites.py   # NSFW平台上傳腳本
    └── integrated_flow.py        # 整合流程腳本
```

## 構建步驟

### 1. 準備環境

確保您的系統已安裝以下軟件：
- Docker
- Docker Compose

### 2. 配置環境變量

從`.env.example`複製創建`.env`文件，並填入您的API密鑰和認證信息：

```bash
cp .env.example .env
```

然後編輯`.env`文件，修改以下環境變量：

```
# Supabase連接信息
SUPABASE_URL=your_supabase_url_here
SUPABASE_API_KEY=your_supabase_api_key_here

# OneDrive API憑證
ONEDRIVE_CLIENT_ID=your_onedrive_client_id_here
ONEDRIVE_CLIENT_SECRET=your_onedrive_client_secret_here
ONEDRIVE_REFRESH_TOKEN=your_onedrive_refresh_token_here

# Tensor.art設置（如需自動登入）
TENSOR_ART_USERNAME=your_username_here
TENSOR_ART_PASSWORD=your_password_here
```

### 3. 準備Supabase數據庫

在Supabase中創建`prompts`表格，包含以下字段：
- id (uuid, primary key)
- character (text)
- clothing (text)
- pose (text)
- scene (text)
- status (text, 預設值為"pending")
- image_url (text, 可為null)
- created_at (timestamp with time zone)

### 4. 構建Docker映像

```bash
docker-compose build
```

### 5. 啟動服務

```bash
docker-compose up -d
```

## 驗證部署

部署完成後，可以通過以下URL訪問n8n界面：
```
http://localhost:5678
```

使用n8n界面可以查看和管理工作流程的執行情況。

## 自定義配置

### 調整定時器頻率

默認情況下，系統每10分鐘執行一次。要調整此設置，請編輯`n8n_workflow.json`中的定時器節點設置。

### 添加更多NSFW平台

要增加支持的NSFW平台，請編輯`scripts/upload_to_nsfw_sites.py`文件中的`NSFW_MONETIZATION_SITES`列表。

### 修改環境變量

如需修改環境配置，可以直接編輯`.env`文件，然後重啟容器：

```bash
docker-compose down
docker-compose up -d
```

## 故障排除

### 日誌查看

您可以通過以下命令查看系統日誌：

```bash
docker-compose logs -f
```

### 常見問題

1. **圖片生成失敗**: 檢查Tensor.art網站是否可訪問，或者Selenium的元素選擇器是否需要更新。

2. **OneDrive上傳失敗**: 驗證您的OneDrive API憑證是否正確配置。

3. **Supabase連接錯誤**: 檢查Supabase URL和API密鑰是否正確。

4. **環境變量未生效**: 確保`.env`文件位於項目根目錄，且權限正確設置。 