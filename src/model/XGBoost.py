import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier # 針對二元分類使用 XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder # 如果目標變數是字串 'yes'/'no' 等

from google.colab import files

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

# 定義特徵 (X) 和目標變數 (y)
X = df.drop('target', axis=1) # 假設 'target' 是您的目標欄位
y = df['target']

# 如果目標變數是字串 (例如 'yes', 'no')，需要進行編碼
# le = LabelEncoder()
# y = le.fit_transform(y) # 將 'yes' 轉換為 1, 'no' 轉換為 0 (或反之，取決於排序)

# --- 2. 處理缺失值 (範例，請根據您的資料調整) ---
# 簡單的填補範例 (用中位數填補數值型缺失值)
# for col in X.columns:
#     if X[col].isnull().any():
#         if X[col].dtype in ['int64', 'float64']:
#             X[col].fillna(X[col].median(), inplace=True)
#         else: # 對於類別型，可以用眾數或創建一個 'Missing' 類別
#             X[col].fillna(X[col].mode()[0], inplace=True)

# --- 3. 處理類別特徵 (如果有的話，且未事先處理) ---
# XGBoost 預設處理數值，對於類別特徵需要 One-Hot Encoding
# X = pd.get_dummies(X, columns=['categorical_feature1', 'categorical_feature2'])

# --- 4. 分割資料集 (訓練集和測試集) ---
# test_size=0.2 表示 20% 的資料用於測試，random_state 確保結果可重現
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
# stratify=y 確保訓練集和測試集中目標變數的類別比例與原始資料集相同，這對於不平衡的二元分類數據很重要。

# --- 5. 建立和訓練 XGBoost 模型 ---
# XGBClassifier 常用參數:
#   objective: 'binary:logistic' (輸出機率) 或 'binary:logitraw' (輸出 log-odds)
#   eval_metric: 'logloss', 'auc', 'error' (分類錯誤率), 'rmse' (回歸) 等
#   use_label_encoder: 在新版本中已棄用，通常設為 False 並手動處理標籤。
#   n_estimators: 樹的數量
#   learning_rate: 學習率 (每次迭代的權重縮減)
#   max_depth: 每棵樹的最大深度
#   subsample: 訓練每棵樹時，採樣的樣本比例
#   colsample_bytree: 訓練每棵樹時，採樣的特徵比例
#   gamma: 執行一個分區所需的最小損失減少量
#   reg_alpha (L1 regularization) 和 reg_lambda (L2 regularization)
#   scale_pos_weight: 處理類別不平衡問題，可設定為 (負類樣本數 / 正類樣本數)

model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss', # 評估指標，對於二元分類，logloss 或 auc 常用
    n_estimators=100,      # 樹的數量
    learning_rate=0.1,     # 學習率
    max_depth=3,           # 樹的最大深度
    random_state=42,
    use_label_encoder=False # 新版本中這個參數通常設為 False
)

print("開始訓練 XGBoost 模型...")
model.fit(X_train, y_train)
print("模型訓練完成。")

# --- 6. 預測和評估模型 ---
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1] # 獲取預測為正類 (1) 的機率

# 計算評估指標
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print(f"\n模型評估結果 (測試集):")
print(f"準確度 (Accuracy): {accuracy:.4f}")
print(f"精確度 (Precision): {precision:.4f}")
print(f"召回率 (Recall): {recall:.4f}")
print(f"F1 分數 (F1 Score): {f1:.4f}")
print(f"ROC AUC: {roc_auc:.4f}")

# --- 7. 查看特徵重要性 (XGBoost 內建) ---
feature_importances = model.feature_importances_
feature_names = X.columns

importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': feature_importances
}).sort_values(by='Importance', ascending=False)

pd.set_option('display.max_rows', None)
print("\n特徵重要性:")
print(importance_df)


# --- 8. (可選) 使用 SHAP 進行更深入的特徵重要性分析 ---
# 需要安裝 shap 函式庫: pip install shap
# import shap

# # 建立 SHAP Explainer
# explainer = shap.TreeExplainer(model)
# # 計算 SHAP 值
# shap_values = explainer.shap_values(X) # 輸出為列表，因為二元分類有兩個類別的 SHAP 值
# # 如果是二元分類，通常我們關心的是正類的 SHAP 值 (索引為 1)
# if isinstance(shap_values, list) and len(shap_values) == 2:
#     shap_values_for_class_1 = shap_values[1]
# else:
#     shap_values_for_class_1 = shap_values # 如果模型輸出只有一維 (如機率)

# # SHAP 摘要圖
# print("\nSHAP Summary Plot (請在新視窗中查看):")
# shap.summary_plot(shap_values_for_class_1, X)

# # SHAP 條形圖 (平均絕對 SHAP 值)
# print("\nSHAP Bar Plot (平均絕對 SHAP 值):")
# shap.summary_plot(shap_values_for_class_1, X, plot_type="bar")

# # 單個預測的 SHAP Waterfall Plot (例如，第一個測試樣本)
# # print("\nSHAP Waterfall Plot for a single prediction (第一個測試樣本):")
# # shap.plots.waterfall(shap.Explanation(
# #     values=shap_values_for_class_1[0],
# #     base_values=explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value,
# #     data=X.iloc[0].values,
# #     feature_names=X.columns.tolist()
# # ))

# # SHAP Dependence Plot (例如，針對 'language_professionalism_score')
# # print("\nSHAP Dependence Plot for 'language_professionalism_score':")
# # shap.dependence_plot("language_professionalism_score", shap_values_for_class_1, X, interaction_index=None)
