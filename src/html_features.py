import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time
from collections import Counter
import ipaddress
import signal
from tqdm import tqdm
from typing import Tuple, Optional
# ====== 可選: 如果需要處理動態內容，請取消註釋以下內容並安裝相關庫 ======
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
# =====================================================================


def get_html_content(url, timeout=20, max_retries=2):
    """
    根據 URL 獲取網頁的完整 HTML 內容，並偵測是否有轉向。
    先使用 requests 爬取，如果內容為空或失敗則使用 Selenium。
    Args:
        url (str): 目標網頁的 URL。
        timeout (int): 請求超時時間 (秒)。
        max_retries (int): 失敗時重試次數。
    Returns:
        tuple[str, bool]: 網頁的 HTML 內容，如果獲取失敗則返回 None。
                           以及一個布林值，表示是否發生了轉向。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.66 Safari/537.36'
    }

    # 第一步：嘗試使用 requests 爬取
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            body_content = soup.find('body')
            # 檢查內容是否為空或過短（可能是動態內容）
            if html_content and len(html_content.strip()) > 100:
                # 檢查頁面內容是否包含 "page not found" 相關關鍵詞
                not_found_keywords = ['page not found', 'error 404', 'page does not exist', '找不到頁面', '頁面不存在']
                matched_keywords = 0
                try:
                  body_text = body_content.get_text(strip=True)
                  body_lower = body_text.lower()

                  # 計算匹配的關鍵詞數量
                  matched_keywords = sum(1 for keyword in not_found_keywords if keyword in body_lower)
                except:
                  html_lower = html_content.lower()

                  # 計算匹配的關鍵詞數量
                  matched_keywords = sum(1 for keyword in not_found_keywords if keyword in html_lower)
                if matched_keywords >= 2:
                    print(f"❌ URL {url} 頁面內容包含 {matched_keywords} 個 'page not found' 相關關鍵詞，直接跳過")
                    return None, False

                print(f"✅ 使用 requests 成功獲取 {url} 的內容")
                return html_content, False
            else:
                print(f"⚠️  requests 獲取的內容為空或過短，將嘗試使用 Selenium")
                break

        except requests.exceptions.HTTPError as e:
            # 檢查是否為 404 或其他 "page not found" 相關錯誤
            if response.status_code == 404:
                print(f"❌ URL {url} 返回 404 錯誤，直接跳過")
                return None, False
            elif response.status_code >= 400:
                print(f"❌ URL {url} 返回 HTTP {response.status_code} 錯誤，直接跳過")
                return None, False
            else:
                print(f"[重試 {attempt+1}/{max_retries}] Requests 獲取 {url} 時發生 HTTP 錯誤: {e}")
                if attempt == max_retries:
                    print(f"❌ Requests 重試 {max_retries} 次後仍然失敗，將嘗試使用 Selenium")
                    break
                time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"[重試 {attempt+1}/{max_retries}] Requests 獲取 {url} 時發生錯誤: {e}")
            if attempt == max_retries:
                print(f"❌ Requests 重試 {max_retries} 次後仍然失敗，將嘗試使用 Selenium")
                break
            time.sleep(1)

    # 第二步：如果 requests 失敗或內容為空，使用 Selenium
    print(f"🔄 開始使用 Selenium 爬取 {url},暫時設為失敗")
    return None, False
    # return _fetch_dynamic_content(url)

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

def extract_html_features(df: pd.DataFrame, url_column: str = 'url') -> pd.DataFrame:
    """
    在 DataFrame 中為指定的 URL 欄位爬取 HTML 內容並創建多個特徵。
    會自動先使用 requests 爬取，如果內容為空則使用 Selenium。

    Args:
        df (pd.DataFrame): 包含 URL 欄位的 DataFrame。
        url_column (str): DataFrame 中包含 URL 的欄位名稱。預設為 'url'。

    Returns:
        pd.DataFrame: 包含新創建特徵欄位的 DataFrame。
    """

    if url_column not in df.columns:
        raise ValueError(f"DataFrame 中未找到指定的 URL 欄位: '{url_column}'")

    # 確保所有 URL 都是字串類型，並處理可能的 NaN
    df[url_column] = df[url_column].astype(str).replace('nan', '')

    # 更新特徵欄位列表，加入兩個轉向特徵
    html_feature_columns = [
        'phish_hints', 'domain_in_brand', 'nb_hyperlinks', 'ratio_intHyperlinks',
        'ratio_extHyperlinks', 'ratio_extRedirection', 'ratio_extErrors',
        'external_favicon', 'links_in_tags', 'ratio_extMedia', 'safe_anchor',
        'empty_title', 'domain_in_title', 'domain_with_copyright',
        'has_meta_refresh', 'has_js_redirect',
        'feature_extracted'  # 新增欄位
    ]

    results = []

    for index, row in df.iterrows():
        url = row[url_column]

        features = {col: 0.0 for col in html_feature_columns}

        if not url:
            features['feature_extracted'] = 0.0
            results.append(features)
            continue

        print(f"正在處理第 {index+1} / {len(df)} 筆 URL: {url}")

        # 設定單個 URL 的最大處理時間（秒）
        max_url_time = 30

        try:
            # --- 關鍵修改：呼叫 get_html_content 並接收兩個返回值 ---
            html_content, has_js_redirect = safe_process_url(url, max_time=120)
        except Exception as e:
            print(f"❌ 處理 URL {url} 時發生未預期錯誤: {e}")
            features['feature_extracted'] = 0.0
            results.append(features)
            continue

        if html_content:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                parsed_url = urlparse(url)
                base_domain = parsed_url.netloc.split(':')[0]
                if base_domain.startswith('www.'):
                    base_domain = base_domain[4:]
                redirect_keywords = ["window.location.href"]
                # --- 新增的偵測邏輯 ---
                # 15. 偵測 meta 轉向
                meta_refresh_tag = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'refresh'})
                if meta_refresh_tag:
                  content = meta_refresh_tag.get("content", "")
                  features['has_meta_refresh'] = 1.0 if "url=" in content.lower() else 0.0  # 確認是 redirect，不是單純 reload
                else:
                  features['has_meta_refresh'] = 0.0

                # 16. 偵測 JavaScript 轉向 (來自 get_html_content 的返回值)
                features['has_js_redirect'] = 1.0 if soup.find("script", string=lambda s: any(k in s for k in redirect_keywords) if s else False) else 0.0
                # ----------------------

                # --- 1. phish_hints: HTML 內容中是否存在常見的釣魚提示詞語 ---
                phish_keywords = ['login', 'signin', 'account update', 'verify account',
                                  'security alert', 'password', 'bank', 'paypal', 'credit card',
                                  '緊急', '驗證', '登入', '帳戶更新', '安全警告', '密碼']
                text_content = soup.get_text().lower()
                features['phish_hints'] = 1 if any(kw in text_content for kw in phish_keywords) else 0.0

                # --- 2. domain_in_brand: 網站內容中提及的品牌名稱是否與域名一致 ---
                # 簡化處理: 檢查域名核心部分是否出現在 meta description, title 或 copyright 中
                # 更精確需要品牌名稱列表或 NLP 實體識別
                brand_match = 0
                domain_parts = base_domain.split('.')
                # 改進域名提取邏輯：處理多級域名
                if len(domain_parts) >= 2:
                    # 對於常見的頂級域名，取倒數第二個部分
                    tld = domain_parts[-1]
                    if tld in ['com', 'org', 'net', 'edu', 'gov', 'mil']:
                        core_domain = domain_parts[-2]
                    else:
                        # 對於其他域名，取倒數第三個部分（如果存在）
                        core_domain = domain_parts[-3] if len(domain_parts) >= 3 else domain_parts[-2]
                else:
                    core_domain = domain_parts[0]

                title_tag = soup.find('title')
                if title_tag and core_domain in title_tag.get_text().lower():
                    brand_match = 1
                elif soup.find('meta', attrs={'name': 'description'}) and core_domain in soup.find('meta', attrs={'name': 'description'})['content'].lower():
                    brand_match = 1
                features['domain_in_brand'] = brand_match


                # --- 3. nb_hyperlinks: 網頁中超連結的總數 ---
                all_links = soup.find_all('a', href=True)
                features['nb_hyperlinks'] = len(all_links)

                # --- 4. ratio_intHyperlinks: 內部超連結的比例 ---
                # --- 5. ratio_extHyperlinks: 外部超連結的比例 ---
                internal_links = 0
                external_links = 0
                for link_tag in all_links:
                    href = link_tag['href']
                    full_url = urljoin(url, href)
                    linked_domain = urlparse(full_url).netloc
                    if linked_domain == parsed_url.netloc:
                        internal_links += 1
                    else:
                        external_links += 1
                total_links_calc = internal_links + external_links
                features['ratio_intHyperlinks'] = internal_links / total_links_calc if total_links_calc > 0 else 0.0
                features['ratio_extHyperlinks'] = external_links / total_links_calc if total_links_calc > 0 else 0.0


                # --- 6. ratio_extRedirection (外部重新導向的比例) ---
                # 檢查外部連結是否包含重定向相關的屬性或JavaScript
                redirect_count = 0
                for link_tag in all_links:
                    href = link_tag['href']
                    if href.startswith('#'):
                        continue
                    full_url = urljoin(url, href)
                    linked_parsed = urlparse(full_url)
                    linked_domain = linked_parsed.netloc
                    is_external = (linked_domain != parsed_url.netloc)

                    if is_external:
                        # 檢查是否有重定向相關的屬性
                        if link_tag.get('onclick') and 'window.location' in link_tag.get('onclick', ''):
                            redirect_count += 1
                        elif link_tag.get('target') == '_blank' and 'redirect' in link_tag.get_text().lower():
                            redirect_count += 1

                features['ratio_extRedirection'] = redirect_count / len(all_links) if all_links else 0.0

                # --- 7. ratio_extErrors (外部連結中返回錯誤的比例) ---
                # 檢查外部連結是否指向明顯錯誤的URL格式
                error_count = 0
                for link_tag in all_links:
                    href = link_tag['href']
                    if href.startswith('#'):
                        continue
                    full_url = urljoin(url, href)
                    linked_parsed = urlparse(full_url)
                    linked_domain = linked_parsed.netloc
                    is_external = (linked_domain != parsed_url.netloc)

                    if is_external:
                        # 檢查是否為明顯錯誤的URL
                        if 'error' in full_url.lower() or '404' in full_url or 'notfound' in full_url.lower():
                            error_count += 1
                        elif not linked_domain or linked_domain == '':
                            error_count += 1

                features['ratio_extErrors'] = error_count / len(all_links) if all_links else 0.0

                # --- 8. external_favicon: 網站是否使用來自外部域名的 Favicon ---
                favicon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
                features['external_favicon'] = 0.0
                if favicon_link and 'href' in favicon_link.attrs:
                    favicon_url = urljoin(url, favicon_link['href'])
                    favicon_domain = urlparse(favicon_url).netloc
                    if favicon_domain != parsed_url.netloc:
                        features['external_favicon'] = 1.0

                # --- 9. links_in_tags: 特定 HTML 標籤（如 <a>、<script>）中連結的數量 ---
                # 這裡統計所有 href 和 src 屬性的連結
                total_links_in_tags = 0
                for tag in soup.find_all(['a', 'script', 'img', 'link', 'iframe', 'form']):
                    if 'href' in tag.attrs:
                        total_links_in_tags += 1
                    if 'src' in tag.attrs:
                        total_links_in_tags += 1
                    if tag.name == 'form' and 'action' in tag.attrs:
                        total_links_in_tags += 1
                features['links_in_tags'] = total_links_in_tags

                # --- 10. ratio_extMedia: 外部媒體（圖片、音頻、視頻）的比例 ---
                media_tags = soup.find_all(['img', 'audio', 'video', 'source'])
                total_media = len(media_tags)
                external_media = 0
                for media_tag in media_tags:
                    src = media_tag.get('src') or media_tag.get('href')
                    if src:
                        media_url = urljoin(url, src)
                        media_domain = urlparse(media_url).netloc
                        if media_domain != parsed_url.netloc:
                            external_media += 1
                features['ratio_extMedia'] = external_media / total_media if total_media > 0 else 0.0

                # --- 11. safe_anchor: 錨點連結是否安全（例如避免指向可疑外部網站） ---
                # 檢查是否有指向 IP 地址、不常見協議或可疑域名的外部連結
                features['safe_anchor'] = 1.0
                suspicious_keywords = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'fb.me', 'is.gd']

                for link_tag in all_links:
                    href = link_tag['href']
                    if href.startswith('#'):
                        continue
                    full_url = urljoin(url, href)
                    linked_parsed = urlparse(full_url)
                    linked_domain = linked_parsed.netloc
                    is_external = (linked_domain != parsed_url.netloc)

                    if is_external:
                        # 檢查是否為IP地址
                        try:
                            ipaddress.ip_address(linked_domain)
                            features['safe_anchor'] = 0.0
                            break
                        except ValueError:
                            pass

                        # 檢查協議是否安全
                        if linked_parsed.scheme not in ['http', 'https', '']:
                            features['safe_anchor'] = 0.0
                            break

                        # 檢查是否為可疑的短網址服務
                        if any(keyword in linked_domain.lower() for keyword in suspicious_keywords):
                            features['safe_anchor'] = 0.0
                            break

                # --- 12. empty_title: 網頁標題是否為空 ---
                features['empty_title'] = 1.0 if not (soup.title and soup.title.string and soup.title.string.strip()) else 0.0

                # --- 13. domain_in_title: 域名是否出現在網頁標題中 ---
                features['domain_in_title'] = 0.0
                if soup.title and soup.title.string:
                    if base_domain in soup.title.string.lower():
                        features['domain_in_title'] = 1.0

                # --- 14. domain_with_copyright: 網站的版權資訊中是否包含域名 ---
                features['domain_with_copyright'] = 0.0

                # 檢查版權文本
                copyright_text = soup.find(text=re.compile(r'©|copyright', re.IGNORECASE))
                if copyright_text and base_domain in copyright_text.lower():
                    features['domain_with_copyright'] = 1.0

                # 檢查footer區域
                footer_tags = soup.find_all(['div', 'footer'], class_=re.compile(r'footer|copyright', re.IGNORECASE))
                for footer in footer_tags:
                    if base_domain in footer.get_text().lower():
                        features['domain_with_copyright'] = 1.0
                        break

                # 檢查所有包含版權相關文字的標籤
                copyright_tags = soup.find_all(text=re.compile(r'©|copyright|all rights reserved', re.IGNORECASE))
                for tag in copyright_tags:
                    if base_domain in tag.lower():
                        features['domain_with_copyright'] = 1.0
                        break

                features['feature_extracted'] = 1.0
            except Exception as e:
                print(f"解析 URL '{url}' 的 HTML 時發生錯誤: {e}")
                features = {col: 0.0 for col in html_feature_columns}
                features['feature_extracted'] = 0.0
        else:
            print(f"未能獲取 URL '{url}' 的 HTML 內容。所有 HTML 特徵將為 0.0。")
            features = {col: 0.0 for col in html_feature_columns}
            features['feature_extracted'] = 0.0
        results.append(features)
        time.sleep(0.5)

    features_df = pd.DataFrame(results, index=df.index)
    df_with_features = pd.concat([df, features_df], axis=1)

    return df_with_features

import signal

class TimeoutException(Exception):
    pass

def handler(signum, frame):
    raise TimeoutException()

def safe_process_url(url, max_time=30):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(max_time)  # 設定最多處理 max_time 秒
    try:
        html_content, has_js_redirect = get_html_content(url, timeout=20, max_retries=1)
        signal.alarm(0)  # 成功就清掉 alarm
        return html_content, has_js_redirect
    except TimeoutException:
        print(f"⏰ URL {url} 超過 {max_time} 秒，強制跳過")
        return None, False
    except Exception as e:
        print(f"❌ URL {url} 處理失敗: {e}")
        return None, False


# --- 範例使用 ---
if __name__ == "__main__":

    df = load_data()
    df = df[42000:52000]
    # 呼叫函式創建新特徵
    # 注意: 會自動先使用 requests，如果內容為空則使用 Selenium
    df_with_html_features = extract_html_features(df, url_column='url')
    # save_df(df_with_html_features, 'output_with_features_5000toEnd.csv')
    print("\n包含新 HTML 特徵的 DataFrame:")
    print(df_with_html_features)

    print("\n所有新創建的 HTML 特徵欄位及其值類型:")
    new_html_cols = [f for f in df_with_html_features.columns if f not in df.columns]
    print({col: df_with_html_features[col].dtype for col in new_html_cols})
