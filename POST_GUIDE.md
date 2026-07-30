# 세븐로그 자동 발행 가이드 (AI 작성용)

이 문서는 매일 새 글을 자동 발행하는 AI 세션이 따라야 할 규칙입니다.

## 1. 오늘의 주제 정하기 (요일 로테이션)

한국 시간(KST) 기준 오늘 요일에 해당하는 카테고리로 글을 씁니다.

| 요일 | 카테고리 | 폴더 |
|------|----------|------|
| 월 | 교육 | content/education |
| 화 | 자동차 | content/car |
| 수 | 여행 | content/travel |
| 목 | 요리 | content/cooking |
| 금 | AI | content/ai |
| 토 | 게임 | content/game |
| 일 | 운동 | content/fitness |

## 2. 주제 선정 규칙

1. 해당 카테고리 폴더의 기존 글 제목(frontmatter title)을 전부 확인하고, **겹치지 않는 새로운 주제**를 고릅니다.
2. 웹 검색으로 해당 분야에서 검색 수요가 있는 주제를 찾습니다. 계절성(여름 휴가, 연말정산 등)이 있으면 반영합니다.
3. 시의성 있는 정보(가격, 정책, 서비스명)는 반드시 웹 검색으로 확인하고, 확인 안 되는 수치는 쓰지 않습니다.

## 3. 글 형식

파일 위치: `content/<카테고리>/<영문-슬러그>.md` (슬러그는 소문자 영문+하이픈)

```
---
title: 제목
date: YYYY-MM-DD (오늘 날짜, KST)
description: 검색결과에 노출될 140~160자 요약문
tags: 태그1, 태그2, 태그3, 태그4
---

본문
```

## 4. 품질 기준

- 공백 포함 3,500자 이상의 실질적 정보
- 구조: 서론 2~3문단 → `##` 소제목 5~7개 → 마지막 `## 자주 묻는 질문(FAQ)` (### 질문 3개)
- 본문에 `#`(H1) 사용 금지
- 표 1개 이상 또는 목록 3개 이상 활용
- "~습니다"체 통일, 과장 표현·클리셰 금지, 사람이 쓴 것처럼 자연스럽게
- 확인 안 된 통계·수치 작성 금지
- 이미지: 아래 "4-1. 이미지 규칙"에 따라 대표 1장 + 본문 3장 삽입
- 건강/운동 글에는 안전 수칙 포함, 의학적 조언으로 오해될 표현 금지

## 4-1. 이미지 규칙 (대표 1장 + 본문 3장)

매 글마다 이미지 4장을 넣습니다: 서론 시작 전에 대표 1장, 본문 소제목 사이에 3장.

**이미지 구하기 (혼합 방식)**

1. **1순위 - 무료 스톡(Wikimedia Commons)**: 실물이 존재하는 주제(요리, 여행, 자동차, 운동 등)는 반드시 실사 사진을 씁니다. 특히 여행 글의 실제 장소는 AI 생성 금지.
   - 검색: `https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch=<검색어>&gsrnamespace=6&gsrlimit=10&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1200` (curl로 호출, 영어·한국어 검색어 병행)
   - 라이선스가 CC0, CC BY, CC BY-SA, Public domain인 것만 사용. `thumburl`(1280px)을 다운로드.
   - 사진이 글 내용과 실제로 맞는지 확인하고, 어긋나면 다른 사진을 고릅니다.
2. **2순위 - AI 생성(Higgsfield MCP)**: 스톡에서 맞는 사진이 없는 추상적 주제(AI, 게임, 교육 개념도 등)만 `generate_image`(model: `nano_banana`, aspect_ratio 16:9, 장당 1크레딧)로 생성 후 결과 URL을 다운로드. 실존 인물·실제 장소·특정 브랜드 제품처럼 오해 소지가 있는 대상은 생성 금지.
3. 둘 다 실패하면 이미지 없이 발행해도 됩니다(빌드 실패보다 낫습니다).

**저장 형식**

- 경로: `content/<카테고리>/img/<글-슬러그>-hero.webp`, `<글-슬러그>-1.webp` ~ `-3.webp`
- Pillow로 변환: 가로 최대 1200px, WEBP quality 75~80, 장당 300KB 이하 목표
- 빌드가 `content/<카테고리>/img/` → `/<카테고리>/img/`로 복사하므로 글에서는 상대경로 `../img/파일명.webp`로 참조

**본문 삽입 형식 (그대로 사용)**

```html
<figure>
<img src="../img/<파일명>.webp" alt="<사진 내용 한국어 설명>" loading="lazy" decoding="async">
<figcaption>사진: <a href="<Commons 파일 페이지 URL>" rel="nofollow"><작성자>, Wikimedia Commons</a> (<라이선스>)</figcaption>
</figure>
```

- 스톡 사진은 위처럼 출처·작성자·라이선스를 반드시 표기합니다.
- AI 생성 이미지는 figcaption을 `AI 생성 이미지`로 표기합니다.
- alt 텍스트는 사진을 못 보는 독자에게 설명하듯 구체적으로 씁니다.

## 5. 발행 절차

1. 글 작성 후 `pip install markdown --break-system-packages && python3 build.py` 로 빌드가 성공하는지 확인합니다.
2. 빌드 성공 시 커밋 & 푸시:
   ```
   git add content/
   git commit -m "post: <글 제목>"
   git push origin main
   ```
3. 푸시하면 GitHub Actions가 자동으로 빌드·배포합니다. 별도 배포 작업은 필요 없습니다.
4. 빌드 실패 시 원인을 수정한 뒤 다시 시도하고, 해결이 안 되면 푸시하지 않습니다.

## 6. 금지 사항

- 기존 글 수정·삭제 금지 (새 글 추가만)
- config.json, build.py, templates/, static/ 수정 금지
- 하루 1편만 발행
