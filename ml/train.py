"""
Module: ml/train.py (Phụ trách: Thành viên A - Task A05)
Chức năng:
  - Huấn luyện và so sánh SVM vs Random Forest trên đặc trưng Librosa MFCC.
  - Tính toán Accuracy, Precision, Recall, F1-score, Equal Error Rate (EER).
  - Lưu model tốt nhất vào ml/saved/model.pkl và ml/saved/scaler.pkl.
"""
import os
import glob
import json
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_curve
from ml.preprocess import ensure_initial_dataset
from ml.features import extract_features_from_file


def compute_eer(y_true, y_scores):
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    fnr = 1 - tpr
    idx = int(np.nanargmin(np.absolute(fnr - fpr)))
    return float(fpr[idx]), float(thresholds[idx])


def train_and_evaluate(real_dir="data/real", fake_dir="data/fake"):
    ensure_initial_dataset()
    X, y = [], []
    for f in sorted(glob.glob(os.path.join(real_dir, "*.wav"))):
        vec, _ = extract_features_from_file(f)
        X.append(vec)
        y.append(0)
    for f in sorted(glob.glob(os.path.join(fake_dir, "*.wav"))):
        vec, _ = extract_features_from_file(f)
        X.append(vec)
        y.append(1)

    X, y = np.array(X), np.array(y)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    candidates = {
        "SVM (RBF Kernel)": SVC(kernel="rbf", C=2.0, probability=True, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, random_state=42),
    }

    metrics_report = {}
    best_model, best_name, best_f1 = None, "", -1.0

    print("\n=== BẢNG SO SÁNH MÔ HÌNH PHÁT HIỆN GIỌNG GIẢ (TASK A05) ===")
    for name, clf in candidates.items():
        clf.fit(X_tr_s, y_tr)
        preds = clf.predict(X_te_s)
        probs = clf.predict_proba(X_te_s)[:, 1]
        acc = accuracy_score(y_te, preds)
        prec, rec, f1, _ = precision_recall_fscore_support(y_te, preds, average="binary", zero_division=0)
        eer, thr = compute_eer(y_te, probs)
        metrics_report[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "eer": round(float(eer), 4),
            "optimal_threshold": round(float(thr), 4),
        }
        print(f"• {name:18s} | Acc={acc:.4f} | Prec={prec:.4f} | Rec={rec:.4f} | F1={f1:.4f} | EER={eer:.4f}")
        if f1 >= best_f1:
            best_f1, best_model, best_name = f1, clf, name

    os.makedirs("ml/saved", exist_ok=True)
    joblib.dump(best_model, "ml/saved/model.pkl")
    joblib.dump(scaler, "ml/saved/scaler.pkl")
    with open("ml/saved/metrics.json", "w", encoding="utf-8") as f:
        json.dump({"best_model": best_name, "models": metrics_report}, f, indent=2, ensure_ascii=False)

    print(f"=> Đã lưu mô hình tốt nhất ({best_name}) vào ml/saved/model.pkl\n")
    return metrics_report


if __name__ == "__main__":
    train_and_evaluate()
