# ==============================================================================
# ORIGINAL REFERENCE CODE 1 (Dùng cho Mục 5.3 Báo cáo: Print out original code)
# Nguồn tham khảo (Reference Site):
#   1. https://github.com/noorchauhan/DeepFake-Audio-Detection-MFCC
#   2. https://github.com/SarthakAgase/DeepFake-Voice-Detection
# Mô tả: Code gốc trích xuất đặc trưng MFCC cơ bản bằng Librosa và phân loại bằng
#        Random Forest / SVM trên tập dữ liệu âm thanh thật/giả.
# ==============================================================================

import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib


def extract_mfcc_features(file_path, n_mfcc=20):
    """
    Hàm gốc từ Reference Site: Chỉ lấy trung bình cộng (mean) của các hệ số MFCC.
    """
    audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)
    mfccs_processed = np.mean(mfccs.T, axis=0)
    return mfccs_processed


def load_data(data_directory):
    features = []
    labels = []
    for label_dir, label_val in [('real', 0), ('fake', 1)]:
        folder = os.path.join(data_directory, label_dir)
        if not os.path.exists(folder):
            continue
        for file_name in os.listdir(folder):
            if file_name.endswith('.wav'):
                file_path = os.path.join(folder, file_name)
                data = extract_mfcc_features(file_path)
                features.append(data)
                labels.append(label_val)
    return np.array(features), np.array(labels)


if __name__ == '__main__':
    X, y = load_data('data')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    joblib.dump(clf, 'rf_model_original.pkl')
