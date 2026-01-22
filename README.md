# E‑Commerce Data Analysis

> **새싹 DX2기 공통 가이드**
> 1. 팀별 [Use this template] 후 본 내용을 프로젝트 실제 내용에 맞춰 수정하세요.
> 2. 원본 데이터는 절대 GitHub에 push하지 않습니다.

## [1] 프로젝트 개요 (Project Overview)

- **분석 상황 (Context)**: 
- **분석 목표 (Objectives)**: [...]
    - [...]
    - [...]
- **핵심 오디언스**: [...]

## [2] 핵심 분석 결과 (Key Findings)
- **인사이트 1**: [...]
- **인사이트 2**: [...]

---

## [3] 프로젝트 구조 및 설정 (Setup & Architecture)

### 📂 폴더 구조
- `data/`: 로컬 원본 데이터 및 전처리된 데이터 저장 (Git 제외)
- `docs/meetings/`: 팀별 회의록 아카이빙 ([TEMPLATE.md](./docs/meetings/TEMPLATE.md) 활용)
- `notebooks/`: EDA 및 시각화 리포팅 (.ipynb)
- `src/`: 데이터 전처리 엔진 및 유틸리티 함수 (.py)
- `reports/figures/`: 최종 분석 결과 시각화 차트

### 🔧 환경 설정
본 프로젝트는 `Python 3.10+` 환경에서 수행됩니다.

```bash
# 가상환경 설정 및 패키지 설치
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## [4] 협업 규칙 (Collaboration & Git Workflow)

### 💬 커뮤니케이션
- **회의록**: 모든 기록은 `./docs/meetings/` 폴더에 `YYYY-MM-DD_제목.md` 형식으로 관리합니다.
- **코드 리뷰**: `main` 브랜치 보호를 위해 반드시 Pull Request 후 승인을 거쳐 Merge 합니다.

### 🚩 Git 커밋 컨벤션
- `[feat]`: 새로운 기능 추가 (전처리 로직 등)
- `[fix]`: 버그 수정
- `[docs]`: 문서 수정 (README, 회의록 등)
- `[refactor]`: 코드 구조 개선

---

## ⚠️ 유의사항
- **데이터 보안**: `.gitignore` 설정에 따라 CSV 파일은 저장소에 업로드되지 않습니다. 공동 작업 시 데이터를 별도로 공유하거나 로컬의 `data/` 폴더에 위치시켜야 합니다.