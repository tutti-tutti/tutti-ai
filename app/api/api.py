from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from collections import Counter
from typing import List
from app.models.schemas import ReviewRequest, FeedbackRequest, ModelSwitchRequest
from app.db.connection import get_db_connection
from app.ml.model_loader import load_model, get_current_model_name
from app.services.sentiment_services import classify, train
from app.services.keyword_services import extract_top_keywords
from app.services.keyword_services import clean_and_tokenize

router = APIRouter()

# 리뷰 분석 및 저장
@router.post("/reviews", tags=["REVIEWS"])
async def analyze_sentiment(request: ReviewRequest):
    sentiment, proba = classify(request.review_text)
    inv_label = {'negative': 0, 'positive': 1}
    y = inv_label[sentiment]
    per_proba = round(proba * 100, 2)

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO review (review, sentiment, probability, date) VALUES (%s, %s, %s, NOW())"
            cursor.execute(query, (request.review_text, y, per_proba))
            conn.commit()
        except Exception as err:
            return JSONResponse(status_code=500, content={"error": f"MySQL 오류: {err}"})
        finally:
            cursor.close()
            conn.close()

    return {
        "review_text": request.review_text,
        "sentiment": sentiment,
        "probability": per_proba
    }

# 피드백 저장 및 학습
@router.post("/feedback", tags=["FEEDBACkS"])
async def feedback(request: FeedbackRequest):
    inv_label = {'negative': 0, 'positive': 1}
    y_original = inv_label[request.sentiment]
    y_corrected = int(not y_original) if request.feedback == 'Incorrect' else y_original

    train(request.review_text, y_corrected)
    sentiment_label = request.sentiment
    corrected_label = 'positive' if y_corrected == 1 else 'negative'

    prob = classify(request.review_text)[1]
    per_prob = round(prob * 100, 2)

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO feedback (review, original_sentiment, corrected_sentiment, feedback_type, probability)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (request.review_text, sentiment_label, corrected_label, request.feedback, per_prob))
            conn.commit()
        except Exception as err:
            return JSONResponse(status_code=500, content={"error": f"MySQL 오류: {err}"})
        finally:
            cursor.close()
            conn.close()

    return {
        "message": "피드백이 저장되고, 모델이 업데이트되었습니다.",
        "original_sentiment": sentiment_label,
        "corrected_sentiment": corrected_label,
        "probability": per_prob
    }

# 피드백 목록 조회
@router.get("/feedbacks", tags=["FEEDBACkS"])
def get_feedbacks(limit: int = 10):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT id, review, original_sentiment, corrected_sentiment, feedback_type, probability, created_at
                FROM feedback
                ORDER BY created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

# 리뷰 키워드 검색
@router.get("/reviews/search-by-keyword", tags=["REVIEWS"])
def search_reviews_by_keyword(keyword: str = Query(..., min_length=1)):
    conn = get_db_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

    try:
        cursor = conn.cursor()
        query = """
            SELECT id, review, sentiment, probability, date
            FROM review
            WHERE review LIKE %s
            ORDER BY date DESC
            LIMIT 100
        """
        keyword_pattern = f"%{keyword}%"
        cursor.execute(query, (keyword_pattern,))
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()

# 감성 분포 통계
@router.get("/reviews/stats/sentiment", tags=["STATISTICS"])
def get_sentiment_distribution():
    conn = get_db_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

    try:
        cursor = conn.cursor()
        query = """
            SELECT sentiment, COUNT(*) as count
            FROM review
            GROUP BY sentiment
        """
        cursor.execute(query)
        results = cursor.fetchall()
        distribution = {row['sentiment']: row['count'] for row in results}
        return distribution
    finally:
        cursor.close()
        conn.close()

# 주간 리뷰 수
@router.get("/reviews/stats/weekly", tags=["STATISTICS"])
def get_weekly_review_stats():
    conn = get_db_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                DATE_FORMAT(date, '%Y-%u주차') AS week, 
                COUNT(*) AS count
            FROM review
            GROUP BY week
            ORDER BY week DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()

# 월별 감성 통계
@router.get("/reviews/stats/monthlysentiment", tags=["STATISTICS"])
def get_monthly_review_stats_sentiment():
    conn = get_db_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                DATE_FORMAT(date, '%Y-%m') AS month,
                sentiment,
                COUNT(*) as count
            FROM review
            GROUP BY month, sentiment
            ORDER BY month DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()

# 월별 리뷰 수
@router.get("/reviews/stats/monthly", tags=["STATISTICS"])
def get_monthly_review_stats():
    conn = get_db_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

    try:
        cursor = conn.cursor()
        query = """
            SELECT DATE_FORMAT(date, '%Y-%m') AS month, COUNT(*) AS count
            FROM review
            GROUP BY month
            ORDER BY month DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()

# 리뷰 수정
@router.put("/reviews/{review_id}", tags=["REVIEWS"])
def update_review(review_id: int, request: ReviewRequest):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        query = "UPDATE review SET review = %s, date = NOW() WHERE id = %s"
        cursor.execute(query, (request.review_text, review_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
        return {"message": "리뷰가 수정되었습니다."}
    finally:
        cursor.close()
        conn.close()

# 리뷰 삭제
@router.delete("/reviews/{review_id}", tags=["REVIEWS"])
def delete_review(review_id: int):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        query = "DELETE FROM review WHERE id = %s"
        cursor.execute(query, (review_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
        return {"message": "리뷰가 삭제되었습니다."}
    finally:
        cursor.close()
        conn.close()

# 여러 리뷰 분석 (배치)
@router.post(
    "/analyze-batch",
    tags=["REVIEWS"],
    summary="Batch Sentiment Analysis for Reviews",
    description="여러 개의 리뷰 텍스트를 한 번에 받아 감성 분석 결과를 반환합니다.",
    response_description="리뷰 리스트의 감성 분석 결과 목록 반환"
)
async def analyze_batch(
    reviews: List[ReviewRequest] = Body(
        example=[
            {"review_text": "배송이 빠르고 만족스러워요."},
            {"review_text": "상품 상태가 별로였습니다."},
            {"review_text": "가격 대비 품질이 괜찮아요."},
            {"review_text": "배송이 늦어서 아쉬웠어요."},
            {"review_text": "포장이 꼼꼼하게 되어 있네요."},
            {"review_text": "재구매 의사 없습니다."},
            {"review_text": "친절한 고객 응대 감사합니다."},
            {"review_text": "불량 제품이 왔어요."},
            {"review_text": "디자인이 예뻐서 마음에 들어요."},
            {"review_text": "교환 처리 빨라서 좋았습니다."}
        ]
    )
):
    results = []
    for review in reviews:
        sentiment, proba = classify(review.review_text)
        results.append({
            "review_text": review.review_text,
            "sentiment": sentiment,
            "probability": round(proba * 100, 2)
        })
    return results

# 리뷰 길이 제한 확인
@router.post("/analyze-length-filter", tags=["REVIEWS"])
async def analyze_with_length_filter(request: ReviewRequest):
    if len(request.review_text) < 10:
        return {"error": "리뷰가 너무 짧습니다."}
    return {"message": "리뷰 길이 통과"}

# 긍정 리뷰에서 키워드 추출
@router.get("/keywords/top-positive", tags=["KEYWORDS"])
def get_top_keywords_from_positive_reviews(limit: int = 5):
    conn = get_db_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

    try:
        cursor = conn.cursor()
        query = """
            SELECT review
            FROM review
            WHERE sentiment = 1
            ORDER BY date DESC
            LIMIT 1000
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        all_keywords = []
        for row in rows:
            review_text = row['review']
            keywords = clean_and_tokenize(review_text)
            all_keywords.extend(keywords)

        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(limit)

        return {
            "top_positive_keywords": [
                {"keyword": k, "count": v} for k, v in top_keywords
            ]
        }

    except pymysql.MySQLError as err:
        return JSONResponse(status_code=500, content={"error": f"MySQL 오류: {err}"})
    finally:
        cursor.close()
        conn.close()


@router.get("/keywords/top-negative", tags=["KEYWORDS"])
def get_top_keywords_from_negative_reviews(limit: int = 5):
    conn = get_db_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})

    try:
        cursor = conn.cursor()
        query = """
            SELECT review
            FROM review
            WHERE sentiment = 0
            ORDER BY date DESC
            LIMIT 1000
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        all_keywords = []
        for row in rows:
            review_text = row['review']
            keywords = clean_and_tokenize(review_text)
            all_keywords.extend(keywords)

        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(limit)

        return {
            "top_negative_keywords": [
                {"keyword": k, "count": v} for k, v in top_keywords
            ]
        }

    except pymysql.MySQLError as err:
        return JSONResponse(status_code=500, content={"error": f"MySQL 오류: {err}"})
    finally:
        cursor.close()
        conn.close()

# 전체 리뷰에서 상위 키워드 추출
@router.get("/keywords/top3", tags=["KEYWORDS"])
def get_top_keywords(limit: int = 3):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT review FROM review ORDER BY date DESC LIMIT 500"
            cursor.execute(query)
            rows = cursor.fetchall()
            reviews = [row['review'] for row in rows]
            top_keywords = extract_top_keywords(reviews, limit)
            return {
                "top_keywords": [{"keyword": k, "count": v} for k, v in top_keywords]
            }
        finally:
            cursor.close()
            conn.close()
    return JSONResponse(status_code=500, content={"error": "DB 연결 실패"})


@router.post(
    "/model/switch",
    tags=["MODELS"],
    summary="Model Swtich",
    description="모델 이름을 전달받아 감성 분석 모델을 실시간으로 변경합니다."
)
async def switch_model(request: ModelSwitchRequest):
    try:
        load_model()(request.model_name)
        return {"message": f"모델 '{request.model_name}'로 변경되었습니다."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 변경 중 오류 발생: {e}")


@router.get("/model/info", tags=["MODELS"])
def get_current_model_info():
    return {"current_model": get_current_model_name()}
