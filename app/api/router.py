from fastapi import APIRouter, Query, Body
from typing import List
from app.models.schemas import ReviewRequest, FeedbackRequest, ModelSwitchRequest
from app.services.review_service import (
    analyze_and_save_review,
    get_reviews_by_keyword,
    update_review_text,
    delete_review_by_id,
    get_sentiment_stats,
    get_weekly_stats,
    get_monthly_sentiment_stats,
    get_monthly_review_stats,
    analyze_batch_reviews,
    check_review_length,
    save_feedback,
    get_recent_feedbacks,
    get_top_positive_keywords,
    get_top_negative_keywords,
    get_top_keywords_overall
)
from app.services.model_service import (
    switch_model, 
    get_model_info
)

router = APIRouter()

# 리뷰 분석 및 저장
@router.post("/reviews", tags=["REVIEWS"])
async def analyze_sentiment(request: ReviewRequest):
    return analyze_and_save_review(request.review_text)

# 리뷰 키워드 검색
@router.get("/reviews/search-by-keyword", tags=["REVIEWS"])
def search_reviews_by_keyword(keyword: str = Query(..., min_length=1)):
    return get_reviews_by_keyword(keyword)

# 리뷰 수정
@router.put("/reviews/{review_id}", tags=["REVIEWS"])
def update_review(review_id: int, request: ReviewRequest):
    return update_review_text(review_id, request.review_text)

# 리뷰 삭제
@router.delete("/reviews/{review_id}", tags=["REVIEWS"])
def delete_review(review_id: int):
    return delete_review_by_id(review_id)

# 여러 리뷰 분석 (배치)
@router.post("/analyze-batch", tags=["REVIEWS"])
async def analyze_batch(reviews: List[ReviewRequest] = Body(...)):
    return analyze_batch_reviews(reviews)

# 리뷰 길이 제한 확인
@router.post("/analyze-length-filter", tags=["REVIEWS"])
async def analyze_with_length_filter(request: ReviewRequest):
    return check_review_length(request.review_text)

# 피드백 저장 및 학습
@router.post("/feedback", tags=["FEEDBACKS"])
async def feedback(request: FeedbackRequest):
    return save_feedback(request)

# 피드백 목록 조회
@router.get("/feedbacks", tags=["FEEDBACKS"])
def get_feedbacks(limit: int = 10):
    return get_recent_feedbacks(limit)

# 감성 분포 통계
@router.get("/reviews/stats/sentiment", tags=["STATISTICS"])
def get_sentiment_distribution():
    return get_sentiment_stats()

# 주간 리뷰 수
@router.get("/reviews/stats/weekly", tags=["STATISTICS"])
def get_weekly_review_stats():
    return get_weekly_stats()

# 월별 감성 통계
@router.get("/reviews/stats/monthlysentiment", tags=["STATISTICS"])
def get_monthly_review_stats_sentiment():
    return get_monthly_sentiment_stats()

# 월별 리뷰 수
@router.get("/reviews/stats/monthly", tags=["STATISTICS"])
def get_monthly_stats_review():
    return get_monthly_review_stats()

# 긍정 리뷰에서 키워드 추출
@router.get("/keywords/top-positive", tags=["KEYWORDS"])
def get_top_keywords_from_positive_reviews(limit: int = 5):
    return get_top_positive_keywords(limit)

# 부정 리뷰에서 키워드 추출
@router.get("/keywords/top-negative", tags=["KEYWORDS"])
def get_top_keywords_from_negative_reviews(limit: int = 5):
    return get_top_negative_keywords(limit)

# 전체 리뷰에서 상위 키워드 추출
@router.get("/keywords/top3", tags=["KEYWORDS"])
def get_top_keywords(limit: int = 3):
    return get_top_keywords_overall(limit)

# 모델 변경
@router.post("/model/switch", tags=["MODELS"])
async def switch_model(request: ModelSwitchRequest):
    return switch_model(request.model_name)

# 현재 모델 정보
@router.get("/model/info", tags=["MODELS"])
def get_current_model_info():
    return get_model_info()
