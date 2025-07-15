FROM python:3.11-slim

WORKDIR /app

# 의존성 파일만 먼저 복사해서 캐시 활용
COPY pyproject.toml ./
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install .

# 실제 소스 복사
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 