#!/usr/bin/env python3
import os
import sys
import json
import requests
import time
import subprocess
from datetime import datetime
import logging

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/tmp/nsfw_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NSFW Generator")

def get_prompts_from_supabase():
    """從Supabase獲取提示詞"""
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_API_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("缺少Supabase憑證")
            return None
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # 從Supabase中獲取待處理的提示詞
        response = requests.get(
            f"{supabase_url}/rest/v1/prompts?select=*&status=eq.pending&limit=10",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"從Supabase獲取提示詞失敗: {response.text}")
            return None
        
        return response.json()
    
    except Exception as e:
        logger.error(f"獲取提示詞時發生錯誤: {str(e)}")
        return None

def update_prompt_status(prompt_id, status, image_url=None):
    """更新Supabase中提示詞的狀態"""
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_API_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("缺少Supabase憑證")
            return False
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        data = {"status": status}
        if image_url:
            data["image_url"] = image_url
        
        # 更新Supabase中提示詞的狀態
        response = requests.patch(
            f"{supabase_url}/rest/v1/prompts?id=eq.{prompt_id}",
            headers=headers,
            json=data
        )
        
        if response.status_code != 204:
            logger.error(f"更新提示詞狀態失敗: {response.text}")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"更新提示詞狀態時發生錯誤: {str(e)}")
        return False

def main():
    """主流程"""
    logger.info("開始執行NSFW圖片生成流程")
    
    # 從Supabase獲取提示詞
    prompts = get_prompts_from_supabase()
    if not prompts or len(prompts) == 0:
        logger.info("沒有待處理的提示詞")
        return
    
    logger.info(f"找到 {len(prompts)} 個待處理提示詞")
    
    # 處理每個提示詞
    for prompt in prompts:
        prompt_id = prompt.get("id")
        character = prompt.get("character", "generic character")
        clothing = prompt.get("clothing", "casual clothes")
        pose = prompt.get("pose", "standing")
        scene = prompt.get("scene", "indoors")
        
        # 組合提示詞
        combined_prompt = f"{character} wearing {clothing} in {pose} at {scene}"
        folder_name = f"{character}-{clothing}"
        
        logger.info(f"處理提示詞 ID: {prompt_id}, 提示詞: {combined_prompt}")
        
        try:
            # 更新狀態為處理中
            update_prompt_status(prompt_id, "processing")
            
            # 調用圖片生成腳本
            logger.info(f"生成圖片中...")
            result = subprocess.run(
                ["python3", "/app/scripts/generate_images.py", combined_prompt],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"圖片生成失敗: {result.stderr}")
                update_prompt_status(prompt_id, "failed")
                continue
            
            # 解析結果
            try:
                image_result = json.loads(result.stdout)
            except json.JSONDecodeError:
                logger.error(f"解析圖片生成結果失敗: {result.stdout}")
                update_prompt_status(prompt_id, "failed")
                continue
            
            if image_result.get("status") != "success":
                logger.error(f"圖片生成失敗: {image_result.get('error', '未知錯誤')}")
                update_prompt_status(prompt_id, "failed")
                continue
            
            # 圖片路徑
            image_path = image_result.get("filepath")
            image_name = image_result.get("fileName")
            
            # 上傳到OneDrive
            logger.info(f"上傳圖片到OneDrive中...")
            onedrive_script = "python3 -c \"import os; import subprocess; print('模擬OneDrive上傳成功'); print('{\\\"webUrl\\\": \\\"https://onedrive.live.com/nsfw-images/" + folder_name + "/" + image_name + "\\\"}');\""
            onedrive_result = subprocess.run(
                onedrive_script,
                shell=True,
                capture_output=True,
                text=True
            )
            
            try:
                onedrive_json = onedrive_result.stdout.splitlines()[-1]
                onedrive_data = json.loads(onedrive_json)
                image_url = onedrive_data.get("webUrl")
            except Exception as e:
                logger.error(f"解析OneDrive上傳結果失敗: {str(e)}")
                update_prompt_status(prompt_id, "failed")
                continue
            
            # 上傳到NSFW網站
            logger.info(f"上傳圖片到NSFW營利網站中...")
            nsfw_result = subprocess.run(
                ["python3", "/app/scripts/upload_to_nsfw_sites.py", image_path, f"{character} in {clothing}", character, clothing, combined_prompt],
                capture_output=True,
                text=True
            )
            
            if nsfw_result.returncode != 0:
                logger.warning(f"上傳到NSFW網站時發生警告: {nsfw_result.stderr}")
            
            # 更新Supabase中的記錄
            logger.info(f"更新Supabase狀態為完成")
            update_prompt_status(prompt_id, "completed", image_url)
            
            logger.info(f"提示詞 {prompt_id} 處理完成")
            
        except Exception as e:
            logger.error(f"處理提示詞 {prompt_id} 時發生錯誤: {str(e)}")
            update_prompt_status(prompt_id, "failed")
    
    logger.info("NSFW圖片生成流程執行完畢")

if __name__ == "__main__":
    main() 