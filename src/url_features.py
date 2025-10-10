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
            # 需要一個 TLD 列表，這裡只做簡單的泛化判斷，更精確需要完整 TLD 列表
            # 獲取 hostname 的 TLD (簡單提取最後一個點之後的部分)
            tld = hostname.split('.')[-1] if '.' in hostname else ''
            features['tld_in_path'] = 1 if tld and tld in path.lower() else 0

            # 31. tld_in_subdomain (頂級域名是否出現在子域名中)
            # 這裡我們假設子域名是 hostname 中 TLD 之前的部分
            subdomains = hostname.split('.')[:-1] if '.' in hostname else []
            features['tld_in_subdomain'] = 0
            if tld:
                for sub in subdomains:
                    if tld in sub.lower():
                        features['tld_in_subdomain'] = 1
                        break

            # 33. nb_subdomains (子域名數量)
            # 簡單計算點號數量 - 1 (假設 TLD 是一個點，IP 地址例外)
            if features['ip'] == 1: # IP 地址沒有子域名概念
                features['nb_subdomains'] = 0
            elif hostname:
                parts = hostname.split('.')
                # 例如: www.example.com -> parts=['www', 'example', 'com'] -> 2個點
                # nb_subdomains = len(parts) - 2 (如果包含 www 和 TLD)
                # 更準確的計算可能需要區分 TLD，這裡簡單計算 hostname 中的點號
                features['nb_subdomains'] = hostname.count('.') # 這會包含 TLD 的點，後面再調整
                # 假設 tld 只有一個點，如 .com, .org。對於 `co.uk` 這種會誤判。
                # 較精確的方式是使用 tldextract 或 publicsuffixlist 庫
                if hostname.count('.') >= 1: #至少有一個點才可能有子域名
                    features['nb_subdomains'] = hostname.count('.') - 1 # 減去 TLD 的點
                    if 'www' in parts[0].lower(): # 如果第一個是www，再減1
                        features['nb_subdomains'] -= 1
                    features['nb_subdomains'] = max(0, features['nb_subdomains']) # 確保不為負
            else:
                features['nb_subdomains'] = 0

            # 32. abnormal_subdomain (子域名是否異常 - 例如多個子域名，或看起來隨機的子域名)
            # 這裡做一個簡單的判斷：如果子域名數量多於2個，且包含非常規字符
            features['abnormal_subdomain'] = 0
            if features['nb_subdomains'] > 2: # 先計算 nb_subdomains
                 # 可以擴展為檢查子域名中的隨機性或特殊字符
                pass


            # 34. prefix_suffix (檢查域名是否有前綴或後綴符號，如 '-')
            # 例如: google-search.com
            features['prefix_suffix'] = 0
            if hostname:
                # 檢查 hostname 本身是否包含 `-` 且不在開頭或結尾
                if '-' in hostname and not hostname.startswith('-') and not hostname.endswith('-'):
                    features['prefix_suffix'] = 1
                # 也可以考慮 path 中的連字符，但題目明確是 "域名"
                # if '-' in path: features['prefix_suffix'] = 1 # 如果要包含路徑

            # 35. path_extension (檢查路徑中是否有檔案副檔名)
            features['path_extension'] = 0
            if path:
                # 查找最後一個點，並確保其後有至少一個非斜線字符
                # 且點不在路徑的開頭或結尾
                match = re.search(r'\.([a-zA-Z0-9]+)$', path)
                if match:
                    features['path_extension'] = 1


            # 39. length_words_raw: URL 中所有單詞的總長度。
            all_url_words = [word for word in word_split_pattern.split(url) if word]
            features['length_words_raw'] = sum(len(word) for word in all_url_words)

            # 40. char_repeat: URL 中是否有重複字元序列。
            # 這裡定義為是否存在連續重複的字符 (例如 "aa", "bbb")
            features['char_repeat'] = 0
            if re.search(r'(.)\1{1,}', url): # 尋找任何字符重複兩次或更多 (aa, bbb)
                features['char_repeat'] = 1

            # 提取 hostname 和 path 中的單詞
            hostname_words = [word for word in word_split_pattern.split(hostname) if word]
            # 將 path, query, fragment 合併後再分割
            path_query_fragment = path + query + fragment
            path_words = [word for word in word_split_pattern.split(path_query_fragment) if word]


            # 42. shortest_word_host: 主機名稱中最短單詞的長度。
            features['shortest_word_host'] = min(len(word) for word in hostname_words) if hostname_words else 0

            # 43. shortest_word_path: 路徑中最短單詞的長度。
            features['shortest_word_path'] = min(len(word) for word in path_words) if path_words else 0

            # 44. longest_words_raw: URL 中最長單詞的長度。
            features['longest_words_raw'] = max(len(word) for word in all_url_words) if all_url_words else 0

            # 45. longest_word_host: 主機名稱中最長單詞的長度。
            features['longest_word_host'] = max(len(word) for word in hostname_words) if hostname_words else 0

            # 46. longest_word_path: 路徑中最長單詞的長度。
            features['longest_word_path'] = max(len(word) for word in path_words) if path_words else 0

            # 47. avg_words_raw: URL 中單詞的平均長度。
            features['avg_words_raw'] = float(features['length_words_raw']) / len(all_url_words) if all_url_words else 0.0

            # 48. avg_word_host: 主機名稱中單詞的平均長度。
            features['avg_word_host'] = float(sum(len(word) for word in hostname_words)) / len(hostname_words) if hostname_words else 0.0

            # 49. avg_word_path: 路徑中單詞的平均長度。
            features['avg_word_path'] = float(sum(len(word) for word in path_words)) / len(path_words) if path_words else 0.0


        except Exception as e:
            # 處理解析 URL 時可能發生的錯誤
            print(f"處理 URL '{url}' 時發生錯誤: {e}")
            features = {col: 0.0 for col in feature_columns} # 錯誤時預設為 0.0

        results.append(features)

    # 將結果轉換為 DataFrame
    features_df = pd.DataFrame(results, index=df.index)

    # 將新特徵合併到原始 DataFrame
    df_with_features = pd.concat([df, features_df], axis=1)

    return df_with_features

# --- 範例使用 ---
if __name__ == "__main__":

    # 呼叫函式創建新特徵
    df_with_new_features = extract_url_features(df, url_column='url')

    print("包含新特徵的 DataFrame:")
    print(df_with_new_features.head()) # 顯示前幾行和所有列
    print("\n所有新創建的特徵欄位及其值類型:")
    for col in [f for f in df_with_new_features.columns if f not in df.columns]:
        print(f"- {col}: {df_with_new_features[col].dtype}")

    # 檢查特定 URL 的特徵
    print("\n檢查第二個 URL (phishing.malicious.xyz) 的特徵:")
    print(df_with_new_features.loc[1, [
        'length_url', 'length_hostname', 'ip', 'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm',
        'nb_and', 'nb_eq', 'nb_www', 'nb_com', 'nb_dslash', 'http_in_path', 'https_token',
        'ratio_digits_url', 'ratio_digits_host', 'punycode', 'port', 'nb_subdomains',
        'path_extension'
    ]])

    print("\n檢查 Punycode URL (xn--h28h.com) 的特徵:")
    print(df_with_new_features.loc[4, [
        'length_url', 'length_hostname', 'ip', 'punycode', 'nb_dots', 'nb_subdomains'
    ]])

    print("\n檢查帶有 Port 的 URL 的特徵:")
    print(df_with_new_features.loc[8, [
        'port'
    ]])
