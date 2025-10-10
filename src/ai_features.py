import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import time
import json
import numpy as np
from typing import Optional, Dict, Any, Tuple
from google.colab import userdata
from google.colab import files
import time
from google.api_core import exceptions # 需要匯入特定的錯誤類型
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- 全域常數設定 ---
# MODEL_NAME = 'gemini-1.5-flash-latest'
# MODEL_NAME = 'gemini-2.0-flash'
MODEL_NAME = 'gemini-2.5-flash-lite-preview-06-17'
# MODEL_NAME = 'gemini-2.0-flash-lite'
# MODEL_NAME = 'gemini-2.5-flash'
# MODEL_NAME = 'gemini-2.5-pro'
DELAY_SECONDS = 6
initial_data = None
# --- 檔案路徑設定 ---
# 您的原始資料集檔案名稱
ORIGINAL_DATA_FILE = 'phishing_dataset_expansion_1.csv'
# 程式會自動建立並更新這個檔案來儲存進度
IN_PROGRESS_FILE = 'phishing_dataset_expansion_1_Gemini.csv'



def setup_gemini() -> Optional[genai.GenerativeModel]:
    """
    設定 Google API 金鑰並初始化 Gemini 模型。
    Returns:
        成功時返回初始化的模型物件，失敗時返回 None。
    """
    print("正在設定 Gemini API...")
    # --- 設定 API 金鑰 (Colab 版本) ---
    try:
        # 從 Colab 的密鑰管理器中讀取 API 金鑰
        api_key = userdata.get('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        generation_config=genai.GenerationConfig(
            temperature=0.4,
            response_mime_type="application/json"
        )
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=generation_config)
        print("✅ Gemini API 設定成功！")
        return model
    except userdata.SecretNotFoundError:
        print("錯誤：找不到名為 'GOOGLE_API_KEY' 的密鑰。請檢查左側「鑰匙」圖示中的設定。")
        exit()
    except Exception as e:
        print(f"設定時發生未知錯誤: {e}")
        exit()

def fetch_webpage_text(url: str) -> Tuple[Optional[str], str]:
    """
    爬取指定 URL 的純文字內容，優先使用靜態爬取，若內容為空則切換至動態爬取。

    Args:
        url: 要爬取的網站 URL。

    Returns:
        tuple: (網頁純文字, 狀態碼)。
            - 成功時返回 (text, 'OK')
            - 靜態爬取但內容為空時返回 (None, 'OK_Empty')
            - 動態爬取成功時返回 (text, 'OK_Dynamic')
            - 失敗時返回 (None, 'Error_XXX')
    """
    # 嘗試靜態爬取
    # text, status = _fetch_static_content(url)

    text, status = _fetch_static_content(url)
    # 如果靜態爬取結果為空，則嘗試動態爬取
    if status == 'OK_Empty':
        # print(f"網頁 {url} 靜態內容為空，暫時跳過...")
        # return text, status
        print(f"網頁 {url} 靜態內容為空，切換至動態爬取...")
        return _fetch_dynamic_content(url)

    return text, status

def _fetch_static_content(url: str) -> Tuple[Optional[str], str]:
    """
    使用 requests 爬取靜態網頁內容。
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers, allow_redirects=False, timeout=10)

        # 在這裡檢查狀態碼，處理重新導向
        if response.status_code == 301 or response.status_code == 302:
            print(f"網頁 {url} 發生重新導向，狀態碼: {response.status_code}")
            return None, f'Redirect_{response.status_code}'
        # # --- 新增的偵錯程式碼 ---
        # print("--- 開始偵測 Response ---")
        # print(f"URL: {response.url}")
        # print(f"狀態碼: {response.status_code}")
        # print("--- 網頁內容 (前 500 字) ---")
        # print(response.text[:500])  # 印出網頁內容的前 500 個字元
        # print("--- 偵測結束 ---")
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        web_text = soup.get_text(separator=' ', strip=True)

        # 檢查頁面是否包含 JavaScript 重新導向指令
        # if soup.find('script', string=lambda s: 'window.location.href' in s if s else False):
        #     print(f"網頁 {url} 偵測到 JavaScript 重新導向")
        #     return None, 'Redirect_JS'

        print(f"網頁 {url} 靜態爬取完成...")
        return (web_text, 'OK') if web_text else (None, 'OK_Empty')

    except requests.exceptions.HTTPError as e:
        # 專門處理 HTTP 錯誤，例如 404, 403, 500
        if e.response.status_code == 404:
            return None, 'Error_404' # 明確標示 404
        else:
            return None, f'Error_HTTP_{e.response.status_code}'

    except requests.exceptions.RequestException as e:
        # 處理其他網路層級的錯誤，例如超時(Timeout)、DNS解析失敗等
        print(f"    ❌ 錯誤: 無法爬取網頁 {url}。錯誤訊息: {e}")
        return None, 'Error_Request'
    except Exception as e:
        # 其他未預期錯誤
        print(f"    ❌ 錯誤: 爬取網頁時發生未知錯誤。錯誤訊息: {e}")
        return None, 'Error_Unknown'

def _fetch_dynamic_content(url: str) -> Tuple[Optional[str], str]:
    """
    使用 Selenium 爬取動態網頁內容。
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless') # 啟用無頭模式，讓瀏覽器在背景運行，不顯示視窗
        chrome_options.add_argument('--no-sandbox') # 避免在 Colab 環境下可能發生的權限問題
        chrome_options.add_argument('--disable-dev-shm-usage') # 解決 /dev/shm 分區空間不足的問題，這在 Docker 或 Colab 中很常見
        chrome_options.add_argument('--disable-gpu') # 禁用 GPU 加速
        chrome_options.add_argument('--disable-setuid-sandbox') # 讓 Chrome 可以在不安全的環境下執行

        # 模擬一個真實的 User-Agent，避免被網站偵測為爬蟲
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"')
        # 指定 Chrome 執行檔路徑，指向我們手動安裝的位置
        chrome_options.binary_location = "/bin/chrome-linux64/chrome"
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        # 等待網頁內容載入，可依據網站特性調整時間
        time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        web_text = soup.get_text(separator=' ', strip=True)

        print(f"網頁 {url} 動態爬取完成...")
        return (web_text, 'OK_Dynamic') if web_text else (None, 'OK_Dynamic_Empty')
    except Exception as e:
        print(f"❌ 錯誤: 使用 Selenium 爬取網頁時發生錯誤。訊息: {e}")
        return None, 'Error_Selenium'
    finally:
        if 'driver' in locals():
            driver.quit()


def analyze_text_with_gemini(model: genai.GenerativeModel, web_text: str) -> Optional[Dict[str, Any]]:

    """
    使用 Gemini 分析文本並回傳結構化的 JSON 特徵。
    Args:
        model: 已初始化的 Gemini 模型物件。
        web_text: 從網頁爬取下來的純文字。
    Returns:
        成功時返回包含語意特徵的字典，失敗時返回 None。
    """
    prompt_template = f"""
    # Role: Cyber Security Analyst

  You are a senior cybersecurity analyst specializing in phishing detection. Your task is to objectively analyze the provided web page text and determine if it exhibits characteristics of a phishing attempt, strictly based on the content provided.

  Based *only* on the text provided, generate a JSON object containing the following features. You must remain objective and provide assessments based solely on observable evidence within the text.

  - `creates_urgency`: (boolean) Does the text create a sense of urgency, pressure, or a deadline for the user to act quickly?
  - `uses_threats`: (boolean) Does the text contain threats, warnings of account suspension, or other negative consequences if the user doesn't act?
  - `requests_sensitive_info`: (boolean) Does the text explicitly or implicitly ask for login credentials (username, password), financial details (credit card numbers), or personal identification?
  - `offers_unrealistic_rewards`: (boolean) Does the text offer prizes, lottery winnings, or other rewards that seem too good to be true?
  - `has_spelling_grammar_errors`: (boolean) Are there noticeable spelling or grammatical errors that are uncharacteristic of a professional website?
  - `impersonated_brand`: (string) What specific brand or company (e.g., "Facebook", "Google", "中華郵政") is the text trying to impersonate? This judgment must be based *solely* on mentions, logos, or design cues implied by the *text description* provided. If no specific brand is clear from the text, return "N/A".
  - `language_professionalism_score`: (numeric, 0-10) Rate the professionalism and grammatical correctness of the text.
      - 0-2: Severely unprofessional, numerous glaring spelling/grammar errors, unclear language.
      - 3-5: Noticeable errors, somewhat unprofessional, but understandable.
      - 6-8: Mostly professional, minor or infrequent errors.
      - 9-10: Highly professional, no discernible errors, official tone.
      - Only assign scores of 0 or 10 if there is overwhelming, undeniable evidence to support such an extreme assessment. Most cases will fall between 2 and 8.
  - `overall_phishing_likelihood_score`: (numeric, 0-10) Based on ALL textual clues (urgency, threats, info requests, rewards, language errors, impersonation), what is the overall likelihood that this is a phishing page?
      - 0-2: Very low likelihood; text appears legitimate or benign.
      - 3-5: Moderate likelihood; some suspicious elements, but not conclusive.
      - 6-8: High likelihood; strong indicators of phishing.
      - 9-10: Extremely high likelihood; undeniable phishing attempt based on text.
      - Assign scores of 0 or 10 only if the evidence for or against phishing is absolute and unequivocal. Favor scores between 2 and 8 for nuanced cases.
  - `summary_of_intent`: (string) A brief, one-sentence summary explaining the likely intent of the page based on its text.

  ---
  # Web Page Text to Analyze:

  {web_text}

  ---
  IMPORTANT INTERNAL CHECK: Before generating the JSON, review your assessment. Ensure each boolean and score is based *strictly* on the provided `web_text` and adheres to the specified scoring criteria and objectivity requirements. If any part of your answer does not meet these standards, re-evaluate and correct it before outputting. Do not include this check in your final JSON output.

  # JSON Output:
  """

    # --- 自動重試機制 ---
    max_retries = 3 # 最多重試 3 次
    base_wait_time = 5 # 基礎等待時間 5 秒

    for i in range(max_retries):
      try:
          response = model.generate_content(prompt_template)
          json_string = response.text.strip().replace('```json', '').replace('```', '')
          return json.loads(json_string), 'OK'
      except exceptions.ResourceExhausted:
        # 429 錯誤，直接回傳失敗狀態，不再重試 (因為通常需要等很久)
        print("    ❌ 錯誤: 收到 429 頻率限制錯誤。放棄此筆資料的 Gemini 分析。")
        return None, 'Error_429_RateLimit'
      except exceptions.ServiceUnavailable as e: # 專門捕捉 503 Service Unavailable 錯誤
              wait_time = base_wait_time * (2 ** i) # 等待時間以指數增長 (5s, 10s, 20s)
              print(f"    ⚠️ 警告: 收到 503 伺服器不可用錯誤。將在 {wait_time} 秒後進行第 {i+1}/{max_retries} 次重試...")
              time.sleep(wait_time)
      except Exception as e:
          print(f"    ❌ 錯誤: Gemini API 分析或 JSON 解析失敗。錯誤訊息: {e}")
          return None, 'Error_JSON_Parse'

    print(f"    ❌ 錯誤: 重試 {max_retries} 次後仍然失敗 (503)。")
    return None, 'Error_503_Retries_Failed'

def process_dataframe(df_batch: pd.DataFrame, model: genai.GenerativeModel) -> pd.DataFrame:
    """
    遍歷 DataFrame，對每個 URL 進行分析並擴充特徵。
    Args:
        df: 原始的 DataFrame。
        model: 已初始化的 Gemini 模型物件。
    Returns:
        擴充了語意特徵後的 DataFrame。
    """
    print("\n🚀 開始處理 DataFrame 中小批次的 URL...\n")
    df_processed = df_batch.copy()


    for index, row in df_processed.iterrows():
        print(f"--- 正在處理第 {index + 1}/{len(df_processed)} 筆資料: {row['url']} ---")

        web_text, fetch_status = safe_process_url(row['url'])

        df_processed.loc[index, 'fetch_status'] = fetch_status

        if not web_text:
            df_processed.loc[index, 'gemini_status'] = 'Skipped_Due_To_Fetch_Error'
            print("    網頁被重新導向或是文本為空。")
            print("    ⏭️ 跳過此筆資料。")
            continue

        semantic_features, gemini_status = analyze_text_with_gemini(model, web_text)
        df_processed.loc[index, 'gemini_status'] = gemini_status
        if not semantic_features:
            print("    ⏭️ 跳過此筆資料。")
            continue

        print("    ✅ 成功取得特徵，正在更新 DataFrame...")
        for key, value in semantic_features.items():
            if key in df_processed.columns:
                df_processed.loc[index, key] = value

        print(f"    ⏰ 處理完成，等待 {DELAY_SECONDS} 秒...\n")
        time.sleep(DELAY_SECONDS)

    return df_processed

def load_data() -> pd.DataFrame:

  uploaded = files.upload()

  for fn in uploaded.keys():
    print('User uploaded file "{name}" with length {length} bytes'.format(
        name=fn, length=len(uploaded[fn])))

  # 將上傳的檔案讀取到 pandas DataFrame 中
  # 假設上傳的檔案是 CSV 格式。如果是其他格式，您可能需要調整讀取函數（例如：pd.read_excel）
  file_name = next(iter(uploaded))
  df = pd.read_csv(file_name)

  # 顯示 DataFrame 的前 5 行
  print("✅ 資料集載入成功！")
  return df

import signal

class TimeoutException(Exception):
    pass

def handler(signum, frame):
    raise TimeoutException()

def safe_process_url(url, max_time=90):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(max_time)  # 設定最多處理 max_time 秒
    try:
        web_text, fetch_status = fetch_webpage_text(url)
        signal.alarm(0)  # 成功就清掉 alarm
        return web_text, fetch_status
    except TimeoutException:
        print(f"⏰ URL {url} 超過 {max_time} 秒，強制跳過")
        return None, 'Error_Connect'
    except Exception as e:
        print(f"❌ URL {url} 處理失敗: {e}")
        return None, 'Error_Unknown'


def main():
    global initial_data
    """
    主函式，負責串連整個處理流程。
    """
    model = setup_gemini()
    if not model:
        return # 如果 API 設定失敗，則結束程式

    BATCH_SIZE = 1000

    # --- 步驟 1: 載入進度 ---
    df = load_data()
    initial_data = df
    if os.path.exists(IN_PROGRESS_FILE):
        print(f"發現處理中檔案，從 '{IN_PROGRESS_FILE}' 載入進度...")
        df = pd.read_csv(IN_PROGRESS_FILE)
    else:
        print(f"未發現處理中檔案，從原始檔 '{ORIGINAL_DATA_FILE}' 開始新任務...")
        try:

            # 預先建立新欄位並填滿 NaN
            new_columns = [
                'gemini_status', #新增的狀態欄位
                'fetch_status', # 新增的狀態欄位
                'creates_urgency', 'uses_threats', 'requests_sensitive_info',
                'offers_unrealistic_rewards', 'has_spelling_grammar_errors',
                'impersonated_brand', 'language_professionalism_score',
                'overall_phishing_likelihood_score', 'summary_of_intent'
            ]
            for col in new_columns:
                df[col] = np.nan
        except FileNotFoundError:
            print(f"❌ 錯誤: 找不到原始資料檔 '{ORIGINAL_DATA_FILE}'。請確認檔案是否存在。")
            return

    # --- 步驟 2: 尋找未完成的任務 ---
    # 用 'overall_phishing_likelihood_score' 作為判斷是否處理過的標記
    unprocessed_mask = df['fetch_status'].isnull()
    unprocessed_df = df[unprocessed_mask]
    # unprocessed_df = df[:1000]
    # unprocessed_df = df[(df['fetch_status'] == 'OK_empty') & (df['gemini_status'] == 'Error_JSON_Parse')].loc[9286:]
    if unprocessed_df.empty:
        print("\n🎉🎉🎉 恭喜！所有資料都已處理完畢！🎉🎉🎉")
        return


    # --- 步驟 3: 選取本次批次 ---

    batch_to_process = unprocessed_df.head(BATCH_SIZE)
    # print(f"本次將處理 {len(batch_to_process)} 筆資料。")
    # start_index = 3690
    # end_index = 3693
    # batch_to_process = df.loc[start_index:end_index +1]

    # --- 步驟 4: 處理批次 ---
    processed_batch = process_dataframe(batch_to_process, model)

    # --- 步驟 5: 更新與儲存 ---
    # 使用 .update() 將處理完的批次的結果，更新回原始的完整 DataFrame 中
    df.update(processed_batch)

    print("="*50)
    print("\n✅ 所有資料處理完畢！")
    print("\n--- 最終擴充後的 DataFrame ---")

    display_columns = ['url', 'target'] + [col for col in df.columns if col not in initial_data]
    print(df[display_columns])

    # 建議：將最終結果儲存到檔案
    try:
        df.to_csv(IN_PROGRESS_FILE, index=False, encoding='utf-8-sig')
        print(f"\n💾 進度已更新並儲存至 '{IN_PROGRESS_FILE}'")
        remaining = len(df[df['overall_phishing_likelihood_score'].isnull()])
        print(f"🟢 目前剩餘 {remaining} 筆資料待處理。")
        num = df[(df['fetch_status'].notna())].shape[0]
        count = df[(df['fetch_status'].notna()) & (df['gemini_status'] != 'OK')].shape[0]
        print(f'"爬取過的{num}筆資料中，{count}筆資料無法爬取到網頁內容。')
    except Exception as e:
        print(f"\n❌ 儲存檔案失敗: {e}")


if __name__ == "__main__":
    main()
