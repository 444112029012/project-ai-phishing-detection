from google.colab import files
import pandas as pd

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
  display(df.head())
  return df
# df = load_data()

def save_df(df, filename = 'phishing_dataset_for_trainning'):
    """
    將指定的 DataFrame 存成 CSV 檔案。

    參數:
    - df: 要儲存的 DataFrame
    - filename: 存檔的檔名（例如 'output.csv'）

    功能:
    - 使用 UTF-8 with BOM 編碼避免中文亂碼
    - 不包含索引欄位
    """
    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 資料已成功儲存至 '{filename}'")
    except Exception as e:
        print(f"❌ 儲存失敗：{e}")
