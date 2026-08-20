# su-portal 패치 노트 — 개발계 대상 (2026-08-20)

## 변경 요약

| 파일 | 상태 | 내용 |
|---|---|---|
| `config/settings.py` | 교체 | SECRET_KEY/DEBUG/ALLOWED_HOSTS 하드코딩 제거 → `.env` 로 이동 |
| `.env.example` | 신규 | 레포용 환경변수 템플릿 (WG_* 항목 포함) |
| `wgclient/__init__.py` | 신규 | Warpgate Admin API 클라이언트 (ensure_* 멱등 패턴) |
| `provisioning/services.py` | 교체 | provision/deprovision 에 Warpgate 등록·해제 통합 |

`[ADDED]` / `[CHANGED]` 주석으로 변경 지점 전부 표시함. 그 외 로직은 손대지 않음.

## 적용 순서 (dev, /opt/su-portal)

```bash
# 0. 백업
sudo cp -r /opt/su-portal /opt/su-portal.bak.$(date +%m%d)

# 1. 파일 배치
#    settings.py            → config/settings.py
#    provisioning_services.py → provisioning/services.py (이름 주의)
#    wgclient/              → wgclient/
#    .env.example           → .env.example

# 2. .env 에 신규 항목 추가 (기존 항목 유지)
#    DJANGO_ALLOWED_HOSTS=210.94.240.180,localhost,127.0.0.1
#    DJANGO_DEBUG=true
#    WG_API_URL=...   WG_TOKEN=...   WG_VERIFY_TLS=false
#    ※ DJANGO_SECRET_KEY 는 .env 에 이미 있음 — 이제 실제로 사용됨

# 3. 부팅 확인 (환경변수 누락 시 여기서 바로 죽는 게 정상)
cd /opt/su-portal && .venv/bin/python manage.py check

# 4. 커밋 전 pem 히스토리 확인 (가장 중요)
git log --all --oneline -- sdk-probe-key.pem
#    출력이 있으면 → push 금지, 히스토리 정리 먼저 (filter-repo)

# 5. 커밋
git add config/settings.py provisioning/services.py wgclient/ .env.example PATCH_NOTES.md
git commit -m "feat: env-based settings + warpgate provisioning integration"
```

## 선행 조건 (코드 배치 전에 필요)

1. **개발계 Warpgate 에서 portal-backend 용 API 토큰 발급** → `.env` 의 `WG_TOKEN`
2. **wgclient 엔드포인트 대조**: `wgclient/__init__.py` 의 경로/인증 헤더를
   `wg_verify.py` 로 검증한 실제 계약과 대조. 다르면 해당 상수만 수정.

## 검증 시나리오 (dev)

```bash
# a. WG 연결 확인
.venv/bin/python -c "from wgclient import get_wg; print(get_wg().status())"

# b. 슬롯 1개 발급 → 워커 처리 → Warpgate 웹터미널에서 student1 로그인
.venv/bin/python manage.py shell -c \
  "from provisioning.services import reserve; print(reserve('test-001'))"
.venv/bin/python manage.py worker          # 별도 터미널
# 워커 로그의 'wg provisioned: student1 / <password>' 로 로그인 테스트

# c. 회수 → Warpgate 에서 target/user 사라졌는지 확인
.venv/bin/python manage.py reclaim --yes
.venv/bin/python -c "from wgclient import get_wg; print(get_wg().status())"
```

## 미결 (오늘 범위 아님)

- 비밀번호 전달 경로: 현재 워커 로그에만 출력. 포털 UI 확정 후 결정 (DB 평문 저장 금지)
- 운영 전환 시: application credential 교체, ALLOWED_HOSTS 운영 도메인, Warpgate own-key 를 OpenStack keypair 등록
- `add_user_role` 의 expiry(학기말 자동 만료)는 wgclient.bind() 에 파라미터로 준비돼 있음 — Phase 1 에서 사용
