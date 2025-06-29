# 🤝 Contributing to TUTTI-AI

이 프로젝트에 기여해주셔서 감사합니다.  
기여를 시작하기 전 아래의 가이드라인을 꼭 읽어주세요.

---

## 📌 코드 기여 전 체크리스트

- 이슈가 없다면 먼저 Issue를 생성해주세요.
- 큰 변경사항은 먼저 Discussion 또는 PR로 제안해주세요.
- 반드시 `dev` 브랜치를 기준으로 작업해주세요.
- 커밋 메시지는 명확하게 작성해주세요.

---

## 🛠️ 개발 환경 설정

```bash
# FastAPI 프로젝트 환경 설정 예시
git clone https://github.com/tutti-tutti/tutti-ai.git
cd tutti-ai  # 실제 클론된 디렉터리 이름으로 이동
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ✏️ 커밋 메시지 규칙

| 유형        | 설명                           |
|-------------|--------------------------------|
| `feat:`     | 새로운 기능 추가               |
| `fix:`      | 버그 수정                      |
| `refactor:` | 리팩토링 (기능 변화 없음)      |
| `docs:`     | 문서 수정                      |
| `test:`     | 테스트 관련 작업               |
| `style:`    | 코드 스타일 수정 (세미콜론, 들여쓰기 등) |

예시:

```
feat: 사용자 로그인 API 구현  
fix: 리뷰 작성 시 NullPointerException 수정
```

---

## 🔀 Pull Request 가이드

- `main` 브랜치가 아닌 `dev` 브랜치로 Pull Request를 보내주세요.
- PR 제목은 간결하게 작성하고, 설명에는 변경 사항과 이유를 자세히 작성해주세요.
- 가능하면 스크린샷, 로그, 테스트 결과를 첨부해주세요.
- 리뷰어를 지정해 주세요. 리뷰 후 머지됩니다.

---

## 💬 질문 또는 제안

궁금한 점이나 제안하고 싶은 내용이 있다면 언제든지 Issue를 열어주세요.  
기여해주셔서 진심으로 감사합니다 🙏
