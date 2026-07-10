# 세븐로그 세팅 가이드 (처음 한 번만 하면 됩니다)

전체 흐름: **① GitHub에 올리기 → ② Pages 켜기 → ③ 주소 반영 → ④ 자동 발행 연결 → ⑤ 애드센스 신청**

---

## ① GitHub 저장소 만들고 올리기 (5분)

1. https://github.com/new 에서 새 저장소 생성
   - 이름: `sevenlog` (다른 이름도 가능)
   - 공개(Public) 선택, README 추가는 체크하지 않기
2. 압축 해제한 이 폴더에서 터미널을 열고:

```bash
git init
git add .
git commit -m "initial: sevenlog blog"
git branch -M main
git remote add origin https://github.com/<내아이디>/sevenlog.git
git push -u origin main
```

> 컴퓨터에 git이 없거나 어렵다면: GitHub 웹에서 저장소 생성 후 "uploading an existing file" 링크로 폴더 전체를 드래그해서 올려도 됩니다. (단, `.github` 폴더가 누락되지 않는지 확인)

## ② GitHub Pages 켜기 (1분)

1. 저장소 → **Settings → Pages**
2. **Source**를 **GitHub Actions**로 선택
3. 저장소 → **Actions** 탭에서 "Build & Deploy" 워크플로우가 초록색으로 끝나면 배포 완료
4. 사이트 주소: `https://<내아이디>.github.io/sevenlog/`

## ③ 사이트 주소 반영 (1분)

`config.json`에서 아래 한 줄을 실제 주소로 수정 후 커밋·푸시:

```json
"base_url": "https://<내아이디>.github.io/sevenlog"
```

> 나중에 커스텀 도메인(예: sevenlog.co.kr)을 연결하면 이 값만 바꾸면 됩니다.
> **애드센스 승인 확률을 높이려면 커스텀 도메인을 강력히 권장합니다** (아래 ⑤ 참고).

## ④ 매일 자동 발행 연결

Claude(이 대화)가 매일 아침 요일별 주제로 글을 써서 저장소에 push하는 방식입니다.
Claude가 push할 수 있도록 **Fine-grained 토큰** 하나만 만들어 주세요.

1. https://github.com/settings/personal-access-tokens/new 접속
2. 설정:
   - Token name: `sevenlog-auto-post`
   - Expiration: 1년 (만료 시 갱신 필요)
   - Repository access: **Only select repositories** → `sevenlog` 선택
   - Permissions → Repository permissions → **Contents: Read and write**
3. 생성된 `github_pat_...` 토큰을 복사해서 Claude 대화에 붙여넣고
   **"저장소 주소는 https://github.com/<내아이디>/sevenlog 이고, 자동 발행 켜줘"** 라고 보내면
   Claude가 매일 아침 7시(한국시간) 자동 발행 스케줄을 활성화합니다.

> 이 토큰은 sevenlog 저장소 하나에만, 파일 쓰기 권한만 갖습니다.
> 글 작성 규칙은 저장소의 `POST_GUIDE.md`에 있으며, 언제든 수정하면 다음 발행부터 반영됩니다.

## ⑤ 애드센스 신청

### 신청 전 체크리스트

- [ ] 글 20편 이상 (초기 14편 + 자동 발행 며칠이면 도달)
- [ ] 개인정보처리방침·소개·문의 페이지 (✅ 이미 포함됨)
- [ ] 사이트 개설 후 최소 2~4주 운영 흔적
- [ ] **커스텀 도메인 연결 권장**: `*.github.io` 하위 주소로는 승인이 어렵거나 불가한 경우가 많습니다.
      도메인(연 1~2만 원)을 구입해 연결하는 것이 사실상 필수입니다.
      (가비아/후이즈/Cloudflare 등에서 구입 → 저장소 Settings → Pages → Custom domain 입력)

### 신청 절차

1. https://adsense.google.com 에서 계정 생성 → 사이트 주소 등록
2. 애드센스가 주는 코드 조각에서 `ca-pub-XXXXXXXXXXXXXXXX` 부분을 복사
3. `config.json`의 `"adsense_client"`에 붙여넣고 커밋·푸시 → 사이트 전체에 자동 삽입됩니다
   ```json
   "adsense_client": "ca-pub-XXXXXXXXXXXXXXXX"
   ```
4. `ads.txt` 파일을 열어 게시자 ID를 넣고 주석(#) 해제 후 커밋·푸시
5. 애드센스에서 "검토 요청" → 보통 며칠~몇 주 소요
6. 승인 후 애드센스 대시보드에서 **자동 광고(Auto ads)** 를 켜면 광고 게재 시작

### 꼭 알아두세요 (중요)

- **AI 대량 생성 콘텐츠 리스크**: 구글은 검색 순위 조작 목적의 "대규모 자동 생성 콘텐츠"를 스팸 정책으로 규제합니다. 자동 발행 글이라도 사람이 주기적으로 검토·수정하고, 직접 쓴 글이나 본인 경험·사진을 섞을수록 승인율과 검색 노출이 좋아집니다. 하루 1편 페이스로 설정한 것도 이 때문입니다.
- **승인 거절은 흔한 일**입니다. 거절 사유(콘텐츠 부족, 정책 위반 등)를 보고 보완해서 재신청하면 됩니다.
- 승인 후에도 **자기 광고 클릭은 절대 금지** (계정 정지 사유)
- 수익 지급은 잔액 $100 도달 시부터, 핀 번호 우편 인증 필요

---

## 운영 팁

- **구글 서치 콘솔 등록**: https://search.google.com/search-console 에 사이트 등록 후 `sitemap.xml` 제출 → 검색 노출 시작. 네이버 서치어드바이저도 함께 등록하면 좋습니다.
- 글 수정: `content/` 폴더의 마크다운 파일을 고치고 push하면 자동 반영
- 자동 발행 멈추기/재개: Claude에게 "자동 발행 꺼줘/켜줘"라고 말하면 됩니다
