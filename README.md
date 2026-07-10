# 세븐로그 (SevenLog)

교육 · 자동차 · 여행 · 요리 · AI · 게임 · 운동, 일곱 가지 주제를 다루는 한국어 블로그입니다.
파이썬 기반의 자체 정적 사이트 생성기로 빌드되며, GitHub Pages로 배포됩니다.

## 구조

```
├── build.py              # 사이트 빌더 (마크다운 → HTML)
├── config.json           # 사이트 설정 (이름, 주소, 애드센스 ID, 카테고리)
├── content/<카테고리>/    # 블로그 글 (마크다운)
├── pages/                # 고정 페이지 (소개, 개인정보처리방침, 문의, 이용약관)
├── templates/            # HTML 템플릿
├── static/               # CSS, 파비콘
├── ads.txt               # 애드센스 ads.txt (승인 후 게시자 ID 입력)
├── POST_GUIDE.md         # 자동 발행 AI가 따르는 작성 규칙
└── .github/workflows/    # 자동 빌드·배포 (GitHub Actions)
```

## 로컬 빌드

```bash
pip install markdown
python3 build.py           # _site/ 에 생성
python3 build.py --serve   # http://localhost:8000 미리보기
```

## 새 글 쓰기

`content/<카테고리>/새글-슬러그.md` 파일을 만들고 push 하면 자동으로 배포됩니다.
글 형식과 품질 기준은 `POST_GUIDE.md` 참고.

## 배포

`main` 브랜치에 push 하면 GitHub Actions가 자동으로 빌드 후 GitHub Pages에 배포합니다.
자세한 초기 설정은 `SETUP_GUIDE.md` 참고.
