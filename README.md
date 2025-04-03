# 圖片生成自動發布系統

一個自動化工作流系統，用於生成圖片並發布到多個營利平台。

## 功能概述

本系統提供以下自動化功能：

1. **定時擷取提示詞**: 每10分鐘從Supabase數據庫自動提取圖片生成提示詞
2. **組合提示詞**: 自動組合角色、服裝、姿勢和場景等元素
3. **生成圖片**: 使用Stable Diffusion通過tensor.art網站生成圖片
4. **圖片存儲**: 自動將生成的圖片上傳到OneDrive 365，並按角色和服裝分類
5. **多平台發布**: 將圖片自動發布到15個可營利的內容平台

## 系統要求

- Docker與Docker Compose
- 網絡連接
- Supabase帳戶
- Microsoft 365帳戶（用於OneDrive存儲）
- 各平台的帳戶（用於發布內容）

## 快速開始

1. 克隆此倉庫
2. 配置環境變量（參見`docker-compose.yml`）
3. 運行`docker-compose up -d`啟動服務
4. 訪問`http://localhost:5678`查看n8n工作流

詳細的安裝和配置說明，請參閱[CONSTRUCTION.md](./CONSTRUCTION.md)。

## 使用指南

### 添加新提示詞

在Supabase的`prompts`表中添加新記錄，包含以下字段：
- `character`: 角色名稱
- `clothing`: 服裝描述
- `pose`: 姿勢描述
- `scene`: 場景描述
- `status`: 設置為"pending"

系統將自動處理狀態為"pending"的記錄。

### 監控工作流

通過n8n界面可以監控工作流的執行情況。每個執行都會記錄生成的圖片和上傳狀態。

### 自定義營利平台

本系統預設支持15個營利平台。您可以根據需要添加或移除平台，具體方法見[CONSTRUCTION.md](./CONSTRUCTION.md)。

## 支持的營利平台

1. Fanvue
2. ManyVids
3. Fansly
4. LoyalFans
5. AdmireMe
6. JustForFans
7. AVN Stars
8. PocketStars
9. Frisk
10. SextPanther
11. ModelCentro
12. IWantClips
13. MFC Share
14. Unlockd
15. APClips

## 故障排除

常見問題和解決方法請參閱[CONSTRUCTION.md](./CONSTRUCTION.md)。

## 免責聲明

本系統僅用於合法的成人內容創作。使用者必須遵守所有相關法律法規，並確保所有內容符合各平台的服務條款。系統開發者不對使用者的內容或行為負責。 
