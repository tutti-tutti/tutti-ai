import numpy as np
from app.ml.model_loader import get_current_model

def classify(document: str):
    label = {0: 'negative', 1: 'positive'}
    vectorizer, clf = get_current_model()
    X = vectorizer.transform([document])
    y = clf.predict(X)[0]
    proba = np.max(clf.predict_proba(X))
    return label[y], proba

def train(document: str, y: int):
    vectorizer, clf = get_current_model()
    X = vectorizer.transform([document])
    clf.partial_fit(X, [y])  # ✅ best_estimator_ 제거
