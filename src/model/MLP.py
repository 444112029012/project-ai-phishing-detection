import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
import numpy as np

# 假設這是您已經準備好的 X 和 y (從您的 prepare_dataset 函數得到)
# X 是一個 DataFrame，y 是一個 Series
# 這裡用一個簡單的範例 DataFrame 模擬您的數據
# df = load_data()

# 使用您的 prepare_dataset 函數
def prepare_dataset(df: pd.DataFrame, target_col: str):
    X = df.drop(columns=[target_col]).copy()
    y = df[target_col].copy()
    return X, y

X, y = prepare_dataset(df, 'target')

# 假設 X (DataFrame) 和 y (Series) 已經是經過標準化的數據
# 且已經從 prepare_dataset 函數中獲取

# 確認特徵數量
num_features = X.shape[1]

# 劃分訓練集、驗證集、測試集
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.2, random_state=42, stratify=y_temp
)

# 將 pandas Series 和 DataFrame 轉換為 numpy array 以便 Keras 使用
# 這一步很重要，因為Keras通常更偏好numpy arrays作為輸入
X_train_np = X_train.to_numpy()
X_val_np = X_val.to_numpy()
X_test_np = X_test.to_numpy()
y_train_np = y_train.to_numpy()
y_val_np = y_val.to_numpy()
y_test_np = y_test.to_numpy()

num_features = 8 # 353
# 構建 MLP 模型 (與之前建議的架構相同)
model = keras.Sequential([
    keras.layers.Input(shape=(num_features,)), # 輸入層
    # keras.layers.Dense(1024, activation=tf.keras.activations.swish),  # tf.keras.activations.gelu relu tf.keras.activations.swish
    # keras.layers.BatchNormalization(), # Batch Normalization 在這裡仍然有用，即使數據已標準化
    # keras.layers.Dropout(0.3),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.3),
    # keras.layers.Dense(128, activation='relu'),
    # keras.layers.Dropout(0.3),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dropout(0.3),
    # keras.layers.Dense(128, activation='relu'),
    # keras.layers.BatchNormalization(),
    # keras.layers.Dropout(0.3),
    # keras.layers.Dense(100, activation='relu'),
    # keras.layers.BatchNormalization(),
    # keras.layers.Dropout(0.2),
    keras.layers.Dense(1, activation='sigmoid') # 輸出層，二元分類
])

model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
              loss='binary_crossentropy',
              metrics=['accuracy'])
# keras.optimizers.Adam(learning_rate=0.0001)
model.summary()

# 定義 Early Stopping
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=9,
    restore_best_weights=True
)

# 定義 ReduceLROnPlateau 回調函數
reduce_lr = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss', # 監控驗證集損失
    factor=0.6,         # 學習率降低的因子 (例如，降低到原來的 20%)
    patience=3,         # 在 val_loss 連續 5 個 Epoch 沒有改善後觸發
    min_lr=0.000001,     # 學習率的最小值
    verbose=1           # 顯示學習率降低的訊息
)

# 訓練模型
history = model.fit(X_train_np, y_train_np,
                    epochs=200,
                    batch_size=16,
                    validation_data=(X_val_np, y_val_np),
                    # callbacks=[early_stopping, reduce_lr],
                    verbose=1)

# 評估模型
loss, accuracy = model.evaluate(X_test_np, y_test_np, verbose=0)
print(f"\n最終測試集 Loss: {loss:.4f}")
print(f"最終測試集 Accuracy: {accuracy:.4f}")
