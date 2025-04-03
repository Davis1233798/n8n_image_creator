#!/usr/bin/env python3
import sys
import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

def generate_image(prompt):
    """
    使用Tensor.art網站生成圖片
    :param prompt: 組合好的提示詞
    :return: 下載的圖片路徑
    """
    # 設置Chrome選項
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 設置下載路徑
    download_dir = "/tmp/downloads"
    os.makedirs(download_dir, exist_ok=True)
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # 初始化WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 訪問Tensor.art網站
        driver.get("https://tensor.art/")
        
        # 等待登入完成 (假設已經有cookie或自動登入)
        time.sleep(5)
        
        # 點擊進入生成頁面
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(@class, 'create-button')]"))
        )
        create_button.click()
        
        # 等待提示詞輸入框
        prompt_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Enter a prompt']"))
        )
        
        # 輸入提示詞
        prompt_input.clear()
        prompt_input.send_keys(prompt)
        
        # 點擊生成按鈕
        generate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate') or contains(@class, 'generate-button')]"))
        )
        generate_button.click()
        
        # 等待圖片生成完成
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@class, 'generated-image') or contains(@alt, 'Generated Image')]"))
        )
        
        # 下載圖片
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download') or contains(@class, 'download-button')]"))
        )
        download_button.click()
        
        # 等待下載完成
        time.sleep(5)
        
        # 獲取最新下載的文件
        list_of_files = os.listdir(download_dir)
        full_path = [os.path.join(download_dir, x) for x in list_of_files if x.endswith('.png') or x.endswith('.jpg')]
        if not full_path:
            raise Exception("下載失敗，沒有找到圖片文件")
            
        latest_file = max(full_path, key=os.path.getctime)
        
        # 生成新的文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = random.randint(1000, 9999)
        new_filename = f"generated_{timestamp}_{random_suffix}.png"
        new_filepath = os.path.join(download_dir, new_filename)
        
        # 重命名文件
        os.rename(latest_file, new_filepath)
        
        return {
            "filepath": new_filepath,
            "fileName": new_filename,
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }
    finally:
        # 關閉瀏覽器
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_images.py \"prompt\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    result = generate_image(prompt)
    print(json.dumps(result))
    sys.exit(0 if result["status"] == "success" else 1) 