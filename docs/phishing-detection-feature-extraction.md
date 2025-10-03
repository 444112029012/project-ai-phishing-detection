# 資料集特徵創建

[![hackmd-github-sync-badge](https://hackmd.io/OF2FB_9mRY2nYiHrbnzmGg/badge)](https://hackmd.io/OF2FB_9mRY2nYiHrbnzmGg)


> 本文件介紹三種不同類型的特徵提取方法，用於網址釣魚檢測的資料集建構

---

## 📋 目錄

- [URL 特徵](#url-特徵)
- [HTML 特徵](#html-特徵)  
- [AI 特徵](#ai-特徵)

---

## 🔗 URL 特徵

### 概述
使用 URL 網址資訊獲取相關欄位，透過分析網址結構、字符組成等來識別可疑網址。

### 📊 特徵欄位列表

#### 基本長度特徵
- **length_url**: URL 總長度
- **length_hostname**: 主機名稱長度

#### 字符統計特徵
- **ip**: 檢查 hostname 是否為 IP 地址
- **nb_dots**: 點號數量
- **nb_hyphens**: 連字號數量
- **nb_at**: @ 符號數量
- **nb_qm**: 問號數量
- **nb_and**: & 符號數量
- **nb_or**: | 符號數量
- **nb_eq**: = 符號數量
- **nb_underscore**: _ 符號數量
- **nb_tilde**: ~ 符號數量
- **nb_percent**: % 符號數量
- **nb_slash**: / 符號數量
- **nb_star**: * 符號數量
- **nb_colon**: : 符號數量
- **nb_comma**: , 符號數量
- **nb_semicolumn**: ; 符號數量
- **nb_dollar**: $ 符號數量
- **nb_space**: 空格數量

#### 域名特徵
- **nb_www**: 檢查是否有 "www"
- **nb_com**: 檢查是否有 ".com"
- **nb_dslash**: 檢查是否有 "//" 且不在協議部分
- **http_in_path**: 檢查路徑中是否有 "http" 或 "https"
- **https_token**: 檢查是否為 HTTPS
- **punycode**: 檢查是否為 Punycode 編碼
- **port**: 檢查是否有指定 Port

#### 比例特徵
- **ratio_digits_url**: URL 中數字的比例
- **ratio_digits_host**: hostname 中數字的比例

#### 域名結構特徵
- **tld_in_path**: 頂級域名是否出現在路徑中
- **tld_in_subdomain**: 頂級域名是否出現在子域名中
- **nb_subdomains**: 子域名數量
- **abnormal_subdomain**: 子域名是否異常
- **prefix_suffix**: 檢查域名是否有前綴或後綴符號
- **path_extension**: 檢查路徑中是否有檔案副檔名

#### 文字特徵
- **length_words_raw**: URL 中所有單詞的總長度
- **char_repeat**: URL 中是否有重複字元序列
- **shortest_word_host**: 主機名稱中最短單詞的長度
- **shortest_word_path**: 路徑中最短單詞的長度
- **longest_words_raw**: URL 中最長單詞的長度
- **longest_word_host**: 主機名稱中最長單詞的長度
- **longest_word_path**: 路徑中最長單詞的長度
- **avg_words_raw**: URL 中單詞的平均長度
- **avg_word_host**: 主機名稱中單詞的平均長度
- **avg_word_path**: 路徑中單詞的平均長度

### 💻 程式碼實作

```python
import pandas as pd
from urllib.parse import urlparse
import ipaddress
import re

def extract_url_features(df: pd.DataFrame, url_column: str = 'url') -> pd.DataFrame:
    """
    在 DataFrame 中為指定的 URL 欄位創建多個特徵。

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

    results = []
    word_split_pattern = re.compile(r'[^a-zA-Z0-9]+')
    
    for index, row in df.iterrows():
        url = row[url_column]
        features = {}

        if not url: # 如果 URL 是空字串，則所有特徵都為 0 或預設值
            results.append({col: 0 for col in feature_columns})
            continue

        try:
            parsed_url = urlparse(url)
            scheme = parsed_url.scheme
            hostname = parsed_url.hostname if parsed_url.hostname else ''
            path = parsed_url.path
            query = parsed_url.query
            fragment = parsed_url.fragment

            # 1. length_url (URL 長度)
            features['length_url'] = len(url)

            # 2. length_hostname (hostname 長度)
            features['length_hostname'] = len(hostname)

            # 3. ip (檢查 hostname 是否為 IP 地址)
            features['ip'] = 0
            if hostname:
                try:
                    ipaddress.ip_address(hostname)
                    features['ip'] = 1
                except ValueError:
                    pass # 不是有效的 IP 地址

            # 4. nb_dots (點號數量)
            features['nb_dots'] = hostname.count('.')

            # 5. nb_hyphens (連字號數量)
            features['nb_hyphens'] = url.count('-')

            # 6. nb_at (@ 符號數量)
            features['nb_at'] = url.count('@')

            # 7. nb_qm (問號數量)
            features['nb_qm'] = url.count('?')

            # 8. nb_and (& 符號數量)
            features['nb_and'] = url.count('&')

            # 9. nb_or (| 符號數量) - 較少見，但仍檢查
            features['nb_or'] = url.count('|')

            # 10. nb_eq (= 符號數量)
            features['nb_eq'] = url.count('=')

            # 11. nb_underscore (_ 符號數量)
            features['nb_underscore'] = url.count('_')

            # 12. nb_tilde (~ 符號數量)
            features['nb_tilde'] = url.count('~')

            # 13. nb_percent (% 符號數量)
            features['nb_percent'] = url.count('%')

            # 14. nb_slash (/ 符號數量)
            features['nb_slash'] = url.count('/')

            # 15. nb_star (* 符號數量)
            features['nb_star'] = url.count('*')

            # 16. nb_colon (: 符號數量)
            features['nb_colon'] = url.count(':')

            # 17. nb_comma (, 符號數量)
            features['nb_comma'] = url.count(',')

            # 18. nb_semicolumn (; 符號數量)
            features['nb_semicolumn'] = url.count(';')

            # 19. nb_dollar ($ 符號數量)
            features['nb_dollar'] = url.count('$')

            # 20. nb_space (空格數量) - 通常 URL 不應該有空格，但為了魯棒性仍檢查
            features['nb_space'] = url.count(' ')

            # 21. nb_www (檢查是否有 "www")
            features['nb_www'] = 1 if 'www' in hostname.lower() else 0

            # 22. nb_com (檢查是否有 ".com") - 這裡只檢查 hostname
            features['nb_com'] = 1 if '.com' in hostname.lower() else 0

            # 23. nb_dslash (檢查是否有 "//" 且不在協議部分)
            features['nb_dslash'] = 1 if '//' in path + query + fragment else 0

            # 24. http_in_path (檢查路徑中是否有 "http" 或 "https")
            features['http_in_path'] = 1 if re.search(r'http[s]?://', path + query + fragment, re.IGNORECASE) else 0

            # 25. https_token (檢查是否為 HTTPS)
            features['https_token'] = 1 if scheme == 'https' else 0

            # 26. ratio_digits_url (URL 中數字的比例)
            digits_in_url = sum(c.isdigit() for c in url)
            features['ratio_digits_url'] = digits_in_url / len(url) if len(url) > 0 else 0

            # 27. ratio_digits_host (hostname 中數字的比例)
            digits_in_host = sum(c.isdigit() for c in hostname)
            features['ratio_digits_host'] = digits_in_host / len(hostname) if len(hostname) > 0 else 0

            # 28. punycode (檢查是否為 Punycode 編碼)
            features['punycode'] = 1 if hostname.startswith('xn--') else 0

            # 29. port (檢查是否有指定 Port)
            features['port'] = 1 if parsed_url.port else 0

            # 30. tld_in_path (頂級域名是否出現在路徑中)
            tld = hostname.split('.')[-1] if '.' in hostname else ''
            features['tld_in_path'] = 1 if tld and tld in path.lower() else 0

            # 31. tld_in_subdomain (頂級域名是否出現在子域名中)
            subdomains = hostname.split('.')[:-1] if '.' in hostname else []
            features['tld_in_subdomain'] = 0
            if tld:
                for sub in subdomains:
                    if tld in sub.lower():
                        features['tld_in_subdomain'] = 1
                        break

            # 32. nb_subdomains (子域名數量)
            if features['ip'] == 1: # IP 地址沒有子域名概念
                features['nb_subdomains'] = 0
            elif hostname:
                parts = hostname.split('.')
                features['nb_subdomains'] = hostname.count('.')
                if hostname.count('.') >= 1:
                    features['nb_subdomains'] = hostname.count('.') - 1
                    if 'www' in parts[0].lower():
                        features['nb_subdomains'] -= 1
                    features['nb_subdomains'] = max(0, features['nb_subdomains'])
            else:
                features['nb_subdomains'] = 0

            # 33. abnormal_subdomain (子域名是否異常)
            features['abnormal_subdomain'] = 0
            if features['nb_subdomains'] > 2:
                pass

            # 34. prefix_suffix (檢查域名是否有前綴或後綴符號)
            features['prefix_suffix'] = 0
            if hostname:
                if '-' in hostname and not hostname.startswith('-') and not hostname.endswith('-'):
                    features['prefix_suffix'] = 1

            # 35. path_extension (檢查路徑中是否有檔案副檔名)
            features['path_extension'] = 0
            if path:
                match = re.search(r'\.([a-zA-Z0-9]+)$', path)
                if match:
                    features['path_extension'] = 1

            # 36. length_words_raw: URL 中所有單詞的總長度
            all_url_words = [word for word in word_split_pattern.split(url) if word]
            features['length_words_raw'] = sum(len(word) for word in all_url_words)

            # 37. char_repeat: URL 中是否有重複字元序列
            features['char_repeat'] = 0
            if re.search(r'(.)\1{1,}', url):
                features['char_repeat'] = 1

            # 提取 hostname 和 path 中的單詞
            hostname_words = [word for word in word_split_pattern.split(hostname) if word]
            path_query_fragment = path + query + fragment
            path_words = [word for word in word_split_pattern.split(path_query_fragment) if word]

            # 38. shortest_word_host: 主機名稱中最短單詞的長度
            features['shortest_word_host'] = min(len(word) for word in hostname_words) if hostname_words else 0

            # 39. shortest_word_path: 路徑中最短單詞的長度
            features['shortest_word_path'] = min(len(word) for word in path_words) if path_words else 0

            # 40. longest_words_raw: URL 中最長單詞的長度
            features['longest_words_raw'] = max(len(word) for word in all_url_words) if all_url_words else 0

            # 41. longest_word_host: 主機名稱中最長單詞的長度
            features['longest_word_host'] = max(len(word) for word in hostname_words) if hostname_words else 0

            # 42. longest_word_path: 路徑中最長單詞的長度
            features['longest_word_path'] = max(len(word) for word in path_words) if path_words else 0

            # 43. avg_words_raw: URL 中單詞的平均長度
            features['avg_words_raw'] = float(features['length_words_raw']) / len(all_url_words) if all_url_words else 0.0

            # 44. avg_word_host: 主機名稱中單詞的平均長度
            features['avg_word_host'] = float(sum(len(word) for word in hostname_words)) / len(hostname_words) if hostname_words else 0.0

            # 45. avg_word_path: 路徑中單詞的平均長度
            features['avg_word_path'] = float(sum(len(word) for word in path_words)) / len(path_words) if path_words else 0.0

        except Exception as e:
            # 處理解析 URL 時可能發生的錯誤
            print(f"處理 URL '{url}' 時發生錯誤: {e}")
            features = {col: 0.0 for col in feature_columns}

        results.append(features)

    # 將結果轉換為 DataFrame
    features_df = pd.DataFrame(results, index=df.index)

    # 將新特徵合併到原始 DataFrame
    df_with_features = pd.concat([df, features_df], axis=1)

    return df_with_features

# 範例使用
if __name__ == "__main__":
    # 呼叫函式創建新特徵
    df_with_new_features = extract_url_features(df, url_column='url')
    
    print("包含新特徵的 DataFrame:")
    print(df_with_new_features.head())
    
    print("\n所有新創建的特徵欄位及其值類型:")
    for col in [f for f in df_with_new_features.columns if f not in df.columns]:
        print(f"- {col}: {df_with_new_features[col].dtype}")
```

---

## 🌐 HTML 特徵

### 概述
使用 HTML 網頁文本獲取相關欄位，透過分析網頁內容、連結結構、轉向行為等來識別可疑網站。

### 📊 特徵欄位列表

#### 轉向檢測特徵
- **has_meta_refresh**: 偵測 meta 轉向
- **has_js_redirect**: 偵測 JavaScript 轉向

#### 內容分析特徵
- **phish_hints**: HTML 內容中是否存在常見的釣魚提示詞語
- **domain_in_brand**: 網站內容中提及的品牌名稱是否與域名一致
- **empty_title**: 網頁標題是否為空
- **domain_in_title**: 域名是否出現在網頁標題中
- **domain_with_copyright**: 網站的版權資訊中是否包含域名

#### 連結分析特徵
- **nb_hyperlinks**: 網頁中超連結的總數
- **ratio_intHyperlinks**: 內部超連結的比例
- **ratio_extHyperlinks**: 外部超連結的比例
- **ratio_extRedirection**: 外部重新導向的比例
- **ratio_extErrors**: 外部連結中返回錯誤的比例
- **safe_anchor**: 錨點連結是否安全（例如避免指向可疑外部網站）

#### 資源分析特徵
- **external_favicon**: 網站是否使用來自外部域名的 Favicon
- **links_in_tags**: 特定 HTML 標籤（如 `<a>`、`<script>`）中連結的數量
- **ratio_extMedia**: 外部媒體（圖片、音頻、視頻）的比例

#### 狀態特徵
- **feature_extracted**: 特徵是否成功提取的標記

### 🛠️ 環境設定

```bash
# 安裝必要套件
pip install google-generativeai
pip install selenium
pip install webdriver-manager
apt-get update
apt install chromium-chromedriver

# 手動安裝與最新 WebDriver 相符的 Chrome 瀏覽器
wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/114.0.5735.90/linux64/chrome-linux64.zip
unzip -q chrome-linux64.zip -d /bin/
```

### 💻 程式碼實作

```python
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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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
                    matched_keywords = sum(1 for keyword in not_found_keywords if keyword in body_lower)
                except:
                    html_lower = html_content.lower()
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
    return _fetch_dynamic_content(url)

def _fetch_dynamic_content(url: str):
    """
    使用 Selenium 爬取動態網頁內容。
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"')
        chrome_options.binary_location = "/bin/chrome-linux64/chrome"
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
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
        'feature_extracted'
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
            # 呼叫 get_html_content 並接收兩個返回值
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
                
                # 偵測 meta 轉向
                meta_refresh_tag = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'refresh'})
                if meta_refresh_tag:
                    content = meta_refresh_tag.get("content", "")
                    features['has_meta_refresh'] = 1.0 if "url=" in content.lower() else 0.0
                else:
                    features['has_meta_refresh'] = 0.0

                # 偵測 JavaScript 轉向
                features['has_js_redirect'] = 1.0 if soup.find("script", string=lambda s: any(k in s for k in redirect_keywords) if s else False) else 0.0

                # phish_hints: HTML 內容中是否存在常見的釣魚提示詞語
                phish_keywords = ['login', 'signin', 'account update', 'verify account',
                                  'security alert', 'password', 'bank', 'paypal', 'credit card',
                                  '緊急', '驗證', '登入', '帳戶更新', '安全警告', '密碼']
                text_content = soup.get_text().lower()
                features['phish_hints'] = 1 if any(kw in text_content for kw in phish_keywords) else 0.0

                # domain_in_brand: 網站內容中提及的品牌名稱是否與域名一致
                brand_match = 0
                domain_parts = base_domain.split('.')
                if len(domain_parts) >= 2:
                    tld = domain_parts[-1]
                    if tld in ['com', 'org', 'net', 'edu', 'gov', 'mil']:
                        core_domain = domain_parts[-2]
                    else:
                        core_domain = domain_parts[-3] if len(domain_parts) >= 3 else domain_parts[-2]
                else:
                    core_domain = domain_parts[0]

                title_tag = soup.find('title')
                if title_tag and core_domain in title_tag.get_text().lower():
                    brand_match = 1
                elif soup.find('meta', attrs={'name': 'description'}) and core_domain in soup.find('meta', attrs={'name': 'description'})['content'].lower():
                    brand_match = 1
                features['domain_in_brand'] = brand_match

                # nb_hyperlinks: 網頁中超連結的總數
                all_links = soup.find_all('a', href=True)
                features['nb_hyperlinks'] = len(all_links)

                # ratio_intHyperlinks: 內部超連結的比例
                # ratio_extHyperlinks: 外部超連結的比例
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

                # ratio_extRedirection (外部重新導向的比例)
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
                        if link_tag.get('onclick') and 'window.location' in link_tag.get('onclick', ''):
                            redirect_count += 1
                        elif link_tag.get('target') == '_blank' and 'redirect' in link_tag.get_text().lower():
                            redirect_count += 1

                features['ratio_extRedirection'] = redirect_count / len(all_links) if all_links else 0.0

                # ratio_extErrors (外部連結中返回錯誤的比例)
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
                        if 'error' in full_url.lower() or '404' in full_url or 'notfound' in full_url.lower():
                            error_count += 1
                        elif not linked_domain or linked_domain == '':
                            error_count += 1

                features['ratio_extErrors'] = error_count / len(all_links) if all_links else 0.0

                # external_favicon: 網站是否使用來自外部域名的 Favicon
                favicon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
                features['external_favicon'] = 0.0
                if favicon_link and 'href' in favicon_link.attrs:
                    favicon_url = urljoin(url, favicon_link['href'])
                    favicon_domain = urlparse(favicon_url).netloc
                    if favicon_domain != parsed_url.netloc:
                        features['external_favicon'] = 1.0

                # links_in_tags: 特定 HTML 標籤中連結的數量
                total_links_in_tags = 0
                for tag in soup.find_all(['a', 'script', 'img', 'link', 'iframe', 'form']):
                    if 'href' in tag.attrs:
                        total_links_in_tags += 1
                    if 'src' in tag.attrs:
                        total_links_in_tags += 1
                    if tag.name == 'form' and 'action' in tag.attrs:
                        total_links_in_tags += 1
                features['links_in_tags'] = total_links_in_tags

                # ratio_extMedia: 外部媒體的比例
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

                # safe_anchor: 錨點連結是否安全
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

                # empty_title: 網頁標題是否為空
                features['empty_title'] = 1.0 if not (soup.title and soup.title.string and soup.title.string.strip()) else 0.0

                # domain_in_title: 域名是否出現在網頁標題中
                features['domain_in_title'] = 0.0
                if soup.title and soup.title.string:
                    if base_domain in soup.title.string.lower():
                        features['domain_in_title'] = 1.0

                # domain_with_copyright: 網站的版權資訊中是否包含域名
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

# 安全處理 URL 的函數
import signal

class TimeoutException(Exception):
    pass

def handler(signum, frame):
    raise TimeoutException()

def safe_process_url(url, max_time=30):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(max_time)
    try:
        html_content, has_js_redirect = get_html_content(url, timeout=20, max_retries=1)
        signal.alarm(0)
        return html_content, has_js_redirect
    except TimeoutException:
        print(f"⏰ URL {url} 超過 {max_time} 秒，強制跳過")
        return None, False
    except Exception as e:
        print(f"❌ URL {url} 處理失敗: {e}")
        return None, False

# 範例使用
if __name__ == "__main__":
    df = load_data()
    df = df[49500:49800]
    
    # 呼叫函式創建新特徵
    df_with_html_features = extract_html_features(df, url_column='url')
    
    print("\n包含新 HTML 特徵的 DataFrame:")
    print(df_with_html_features)

    print("\n所有新創建的 HTML 特徵欄位及其值類型:")
    new_html_cols = [f for f in df_with_html_features.columns if f not in df.columns]
    print({col: df_with_html_features[col].dtype for col in new_html_cols})
```

---

## 🤖 AI 特徵

### 概述
使用 HTML 網頁文本推送給 GEMINI 獲取相關欄位，透過 AI 分析網頁內容的語意特徵來識別釣魚網站。

### 📊 特徵欄位列表

#### 行為分析特徵
- **creates_urgency**: 文本是否創造緊迫感、壓力或行動期限
- **uses_threats**: 文本是否包含威脅、帳戶暫停警告或其他負面後果
- **requests_sensitive_info**: 文本是否明確或隱含地要求登入憑證、財務詳情或個人身份資訊
- **offers_unrealistic_rewards**: 文本是否提供看似不切實際的獎勵、獎品或彩票中獎

#### 品質分析特徵
- **has_spelling_grammar_errors**: 是否存在明顯的拼寫或語法錯誤，不符合專業網站特徵
- **language_professionalism_score**: 文本的專業性和語法正確性評分 (0-10分)

#### 身份分析特徵
- **impersonated_brand**: 文本試圖冒充的特定品牌或公司名稱
- **overall_phishing_likelihood_score**: 基於所有文本線索的整體釣魚可能性評分 (0-10分)
- **summary_of_intent**: 基於文本內容的頁面意圖簡要總結

#### 狀態特徵
- **fetch_status**: 網頁內容爬取狀態
- **gemini_status**: Gemini API 分析狀態

### 🛠️ 環境設定

```bash
# 安裝必要套件
pip install google-generativeai
pip install selenium
pip install webdriver-manager
apt-get update
apt install chromium-chromedriver

# 手動安裝與最新 WebDriver 相符的 Chrome 瀏覽器
wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/114.0.5735.90/linux64/chrome-linux64.zip
unzip -q chrome-linux64.zip -d /bin/
```

### 💻 程式碼實作

```python
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
from google.api_core import exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- 全域常數設定 ---
MODEL_NAME = 'gemini-2.5-flash'
DELAY_SECONDS = 6
initial_data = None

# --- 檔案路徑設定 ---
ORIGINAL_DATA_FILE = 'phishing_dataset_expansion_1.csv'
IN_PROGRESS_FILE = 'phishing_dataset_expansion_1_Gemini.csv'

def setup_gemini() -> Optional[genai.GenerativeModel]:
    """
    設定 Google API 金鑰並初始化 Gemini 模型。
    Returns:
        成功時返回初始化的模型物件，失敗時返回 None。
    """
    print("正在設定 Gemini API...")
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
    text, status = _fetch_static_content(url)
    
    # 如果靜態爬取結果為空，則嘗試動態爬取
    if status == 'OK_Empty':
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

        # 檢查狀態碼，處理重新導向
        if response.status_code == 301 or response.status_code == 302:
            print(f"網頁 {url} 發生重新導向，狀態碼: {response.status_code}")
            return None, f'Redirect_{response.status_code}'
        
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        web_text = soup.get_text(separator=' ', strip=True)

        print(f"網頁 {url} 靜態爬取完成...")
        return (web_text, 'OK') if web_text else (None, 'OK_Empty')

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None, 'Error_404'
        else:
            return None, f'Error_HTTP_{e.response.status_code}'

    except requests.exceptions.RequestException as e:
        print(f"    ❌ 錯誤: 無法爬取網頁 {url}。錯誤訊息: {e}")
        return None, 'Error_Request'
    except Exception as e:
        print(f"    ❌ 錯誤: 爬取網頁時發生未知錯誤。錯誤訊息: {e}")
        return None, 'Error_Unknown'

def _fetch_dynamic_content(url: str) -> Tuple[Optional[str], str]:
    """
    使用 Selenium 爬取動態網頁內容。
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"')
        chrome_options.binary_location = "/bin/chrome-linux64/chrome"
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
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

    # 自動重試機制
    max_retries = 3
    base_wait_time = 5

    for i in range(max_retries):
        try:
            response = model.generate_content(prompt_template)
            json_string = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(json_string), 'OK'
        except exceptions.ResourceExhausted:
            print("    ❌ 錯誤: 收到 429 頻率限制錯誤。放棄此筆資料的 Gemini 分析。")
            return None, 'Error_429_RateLimit'
        except exceptions.ServiceUnavailable as e:
            wait_time = base_wait_time * (2 ** i)
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

    file_name = next(iter(uploaded))
    df = pd.read_csv(file_name)

    print("✅ 資料集載入成功！")
    return df

# 安全處理 URL 的函數
import signal

class TimeoutException(Exception):
    pass

def handler(signum, frame):
    raise TimeoutException()

def safe_process_url(url, max_time=90):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(max_time)
    try:
        web_text, fetch_status = fetch_webpage_text(url)
        signal.alarm(0)
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
        return

    BATCH_SIZE = 500

    # 載入進度
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
                'gemini_status',
                'fetch_status',
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

    # 尋找未完成的任務
    unprocessed_mask = df['fetch_status'].isnull()
    unprocessed_df = df[unprocessed_mask]
    
    if unprocessed_df.empty:
        print("\n🎉🎉🎉 恭喜！所有資料都已處理完畢！🎉🎉🎉")
        return

    # 選取本次批次
    batch_to_process = unprocessed_df.head(BATCH_SIZE)

    # 處理批次
    processed_batch = process_dataframe(batch_to_process, model)

    # 更新與儲存
    df.update(processed_batch)

    print("="*50)
    print("\n✅ 所有資料處理完畢！")
    print("\n--- 最終擴充後的 DataFrame ---")

    display_columns = ['url', 'target'] + [col for col in df.columns if col not in initial_data]
    print(df[display_columns])

    # 將最終結果儲存到檔案
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
```

---

## 📝 總結

本文件介紹了三種不同類型的特徵提取方法：

### 🔗 URL 特徵 (45個特徵)
- **基本長度特徵**: URL 和 hostname 長度
- **字符統計特徵**: 各種符號的數量統計
- **域名特徵**: 域名結構和協議相關特徵
- **比例特徵**: 數字字符比例
- **文字特徵**: 單詞長度統計

### 🌐 HTML 特徵 (17個特徵)
- **轉向檢測**: Meta 和 JavaScript 轉向
- **內容分析**: 釣魚提示詞、品牌一致性
- **連結分析**: 內外部連結比例和安全性
- **資源分析**: 外部資源使用情況
- **狀態特徵**: 特徵提取成功標記

### 🤖 AI 特徵 (11個特徵)
- **行為分析**: 緊迫感、威脅、敏感資訊請求
- **品質分析**: 語言專業性評分
- **身份分析**: 品牌冒充和整體釣魚可能性
- **狀態特徵**: 爬取和分析狀態追蹤

每種特徵都有完整的程式碼實作，包含錯誤處理、重試機制和進度保存功能，適合用於大規模資料集的釣魚網站檢測任務。


