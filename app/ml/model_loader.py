import os
import joblib

# 프로젝트 루트 기준 object 폴더 경로
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
object_dir = os.path.join(project_root, "object")

# 전역 모델 객체
vectorizer = None
clf = None
current_model_name = "default"  # 기본값

def load_model(model_name: str = ""):
    """
    모델명 없으면 기본 모델 로딩.
    예: model_name = 'okt' → tfidf_vectorizer_okt.joblib
    """
    global vectorizer, clf, current_model_name

    suffix = f"_{model_name}" if model_name else ""
    vec_path = os.path.join(object_dir, f"tfidf_vectorizer{suffix}.joblib")
    model_path = os.path.join(object_dir, f"sentiment_model{suffix}.joblib")

    if not os.path.exists(vec_path) or not os.path.exists(model_path):
        raise FileNotFoundError(f"모델 파일이 존재하지 않습니다: {vec_path}, {model_path}")

    vectorizer = joblib.load(vec_path)
    clf = joblib.load(model_path)
    current_model_name = model_name or "default"

    print(f"모델 '{current_model_name}' 로드 완료!")

def get_current_model():
    """현재 로드된 모델 및 벡터라이저 반환"""
    return vectorizer, clf

def get_current_model_name():
    """현재 모델 이름 반환"""
    return current_model_name

# 서버 시작 시 기본 모델 로딩
load_model()
