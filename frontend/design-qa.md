# KOY 방문객 MVP Design QA

검증일: 2026-08-12  
기준 화면: Figma `provenance-home-scan` (`9:7`), `provenance-docent-qa-bottomsheet` (`28:70`) 및 관련 방문객 프레임  
검증 뷰포트: **375 × 812**

## 실제 검증 증거

- 홈: `qa-screenshots/home.png`
- 제품 스캔: `qa-screenshots/scan.png`
- 제품 헤리티지: `qa-screenshots/heritage.png`
- 도슨트 스토리 및 관심사: `qa-screenshots/story.png`
- 도슨트 Q&A: `qa-screenshots/qa.png`
- Figma 홈 원본은 `get_design_context(9:7)`의 375 × 812 렌더와 직접 비교했다.

## 비교 결과

### 홈

- Figma 수치에 맞춰 상단 내비게이션 56px, 좌우 패딩 24px, CTA 외곽 176px/내부 152px, 카드 폭 156px/이미지 높이 96px, 하단 내비게이션 84px를 적용했다.
- 색상은 원본 토큰 `#F7F3EC`, `#7A4A2B`, `#B08D57`, `#A69C8E`, `#E0D9CD`, `#1F1B18`을 사용한다.
- 하단 항목을 Figma와 동일하게 `홈 / 보관함 / 마이페이지`로 복원했다.
- Figma에서 내려받은 실제 제품 이미지 4개를 `public/figma-product-*.png`로 로컬 저장했다.

### 스캔·헤리티지·스토리

- 375 × 812에서 헤더, 스캔 가이드, 포커스 프레임, 촬영 버튼이 잘리지 않는다.
- 헤리티지는 세로 스크롤로 전체 본문과 CTA에 접근할 수 있다.
- 스토리 관심사는 별도 페이지 없이 `소재 / 장인 공정 / 브랜드 역사` 버튼으로 제공한다. 초기 선택은 `장인 공정`이며 선택 시 제목과 본문이 실제 변경됨을 브라우저에서 확인했다.

### Q&A

- Figma의 528px 하단 시트 구조, 닫기 버튼, 대화 스크롤, 하단 입력창을 재현했다.
- 추천 질문 클릭과 직접 입력 질문이 사용자 메시지로 누적된다.
- `이 가방의 소재는 어디서 온 건가요?`는 `소재` 근거 답변을 표시한다.
- `이 제품의 출시 가격은 얼마인가요?`는 `현재 검수된 아카이브에서는 해당 내용을 확인할 수 없습니다.`와 `근거 부족` 표식을 표시한다.
- 전송 중 상태와 중복 전송 방지를 확인했다.

## 기술 검증

- 패키지 관리자: npm으로 통일. `package-lock.json` 유지, pnpm 잠금/워크스페이스 파일 제거, `npm ci` 성공, 취약점 0개.
- TypeScript: `npx tsc --noEmit` 성공.
- ESLint: `npm run lint` 성공. 오류 0개, `<img>` 최적화 권고 4건만 존재.
- Production build: `npm run build` 성공.
- Development server: 새 서버에서 `/` HTTP 200, Next 준비 및 GET 로그 정상.
- 브라우저 핵심 흐름: 홈 → 스캔 → 인식 중 → 성공 → 헤리티지 → 관심사 변경 → Q&A → 근거 답변 → 근거 부족 답변 통과.
- 브라우저 콘솔: error/warn 0건.
- UTF-8: `page.tsx`, `layout.tsx`의 본문·metadata·alt·aria-label·placeholder를 확인했으며 깨진 한국어 문자열 0건.

## 잔여 P3

- Next ESLint의 `<img>` 최적화 권고가 4건 남아 있다. Figma 원본 비율을 그대로 유지하기 위해 현재는 로컬 `<img>`를 사용하며 기능·접근성·레이아웃에는 영향이 없다.
- 스캔 배경은 Figma 내 카메라 목 화면과 같은 구도를 위한 외부 이미지다. 실제 카메라 연동 시 교체 대상이다.

P0: 0  
P1: 0  
P2: 0  

final result: passed
