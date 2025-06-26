from fastapi import HTTPException
from app.ml.model_loader import load_model, get_current_model_name
from app.db.connection import get_db_connection
from app.db.queries import MODEL_HISTORY_INSERT

def switch_model(model_name: str):
    try:
        load_model()(model_name)

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(MODEL_HISTORY_INSERT, (model_name,))
                    conn.commit()
            finally:
                conn.close()

        return {"message": f"모델 '{model_name}'로 변경되었습니다."}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 변경 중 오류 발생: {e}")

def get_model_info():
    return {"current_model": get_current_model_name()}
