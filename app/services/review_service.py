import numpy as np
from typing import List
from collections import Counter
from konlpy.tag import Okt
from app.ml.model_loader import get_current_model
from app.db.context import with_db_cursor
from app.db import queries as q
from app.models.schemas import FeedbackRequest, ReviewRequest


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
    clf.partial_fit(X, [y])  # best_estimator_ 제거

okt = Okt()
stopwords = {'상품', '쇼핑몰', '정말', '도대체', '이거', '그냥', '너무', '완전', '진짜', '때문'}

def clean_and_tokenize(text: str) -> List[str]:
    text = text.lower()
    tokens = okt.pos(text, stem=True)
    keywords = [
        word for word, tag in tokens
        if tag in ('Noun', 'Adjective') and word not in stopwords and len(word) > 1
    ]
    return keywords

def extract_top_keywords(reviews: List[str], limit: int = 3):
    all_keywords = []
    for review_text in reviews:
        keywords = clean_and_tokenize(review_text)
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    return keyword_counts.most_common(limit)

def analyze_and_save_review(review_text: str):
    sentiment, proba = classify(review_text)
    y = 1 if sentiment == "positive" else 0
    per_proba = round(proba * 100, 2)

    with with_db_cursor(commit=True) as cursor:
        cursor.execute(q.REVIEW_INSERT, (review_text, y, per_proba))

    return {
        "review_text": review_text,
        "sentiment": sentiment,
        "probability": per_proba
    }


def get_reviews_by_keyword(keyword: str):
    pattern = f"%{keyword}%"
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_REVIEW_BY_KEYWORD, (pattern,))
        return cursor.fetchall()


def update_review_text(review_id: int, new_text: str):
    with with_db_cursor(commit=True) as cursor:
        cursor.execute(q.REVIEW_UPDATE, (new_text, review_id))
        if cursor.rowcount == 0:
            raise ValueError("리뷰를 찾을 수 없습니다.")
    return {"message": "리뷰가 수정되었습니다."}


def delete_review_by_id(review_id: int):
    with with_db_cursor(commit=True) as cursor:
        cursor.execute(q.REVIEW_DELETE, (review_id,))
        if cursor.rowcount == 0:
            raise ValueError("리뷰를 찾을 수 없습니다.")
    return {"message": "리뷰가 삭제되었습니다."}


def get_sentiment_stats():
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_SENTIMENT_STATS)
        result = cursor.fetchall()
        return {row["sentiment"]: row["count"] for row in result}


def get_weekly_stats():
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_WEEKLY_STATS)
        return cursor.fetchall()


def get_monthly_sentiment_stats():
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_MONTHLY_SENTIMENT_STATS)
        return cursor.fetchall()


def get_monthly_review_stats():
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_MONTHLY_REVIEW_STATS)
        return cursor.fetchall()


def analyze_batch_reviews(reviews: List[ReviewRequest]):
    results = []
    for review in reviews:
        sentiment, proba = classify(review.review_text)
        results.append({
            "review_text": review.review_text,
            "sentiment": sentiment,
            "probability": round(proba * 100, 2)
        })
    return results


def check_review_length(text: str):
    if len(text) < 10:
        return {"error": "리뷰가 너무 짧습니다."}
    return {"message": "리뷰 길이 통과"}


def save_feedback(request: FeedbackRequest):
    inv_label = {"negative": 0, "positive": 1}
    y_original = inv_label[request.sentiment]
    y_corrected = int(not y_original) if request.feedback == "Incorrect" else y_original

    train(request.review_text, y_corrected)
    corrected_label = "positive" if y_corrected == 1 else "negative"
    prob = classify(request.review_text)[1]
    per_prob = round(prob * 100, 2)

    with with_db_cursor(commit=True) as cursor:
        cursor.execute(
            q.FEEDBACK_INSERT,
            (request.review_text, request.sentiment, corrected_label, request.feedback, per_prob)
        )

    return {
        "message": "피드백이 저장되고, 모델이 업데이트되었습니다.",
        "original_sentiment": request.sentiment,
        "corrected_sentiment": corrected_label,
        "probability": per_prob
    }


def get_recent_feedbacks(limit: int = 10):
    with with_db_cursor() as cursor:
        cursor.execute(q.FEEDBACK_SELECT_RECENT, (limit,))
        return cursor.fetchall()


def get_top_positive_keywords(limit: int = 5):
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_POSITIVE_REVIEWS)
        reviews = [row["review"] for row in cursor.fetchall()]
        keywords = sum([clean_and_tokenize(r) for r in reviews], [])
        counts = Counter(keywords).most_common(limit)
        return {"top_positive_keywords": [{"keyword": k, "count": v} for k, v in counts]}


def get_top_negative_keywords(limit: int = 5):
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_NEGATIVE_REVIEWS)
        reviews = [row["review"] for row in cursor.fetchall()]
        keywords = sum([clean_and_tokenize(r) for r in reviews], [])
        counts = Counter(keywords).most_common(limit)
        return {"top_negative_keywords": [{"keyword": k, "count": v} for k, v in counts]}


def get_top_keywords_overall(limit: int = 3):
    with with_db_cursor() as cursor:
        cursor.execute(q.GET_ALL_REVIEWS)
        reviews = [row["review"] for row in cursor.fetchall()]
        top_keywords = extract_top_keywords(reviews, limit)
        return {"top_keywords": [{"keyword": k, "count": v} for k, v in top_keywords]}

