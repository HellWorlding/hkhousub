# 아파트 청약 서비스 — 명세서 (Specification / PRD)

> MVP 수준. Django 6 + Django REST Framework(DRF) + PostgreSQL.
> PK는 **UUID**를 사용한다. 스프링 경험자를 위한 개념 대응을 함께 표기한다.

---

## 1. 개요

아파트 **청약(subscription)** 을 관리하는 REST API 서비스.
회원이 특정 아파트(주택형)에 청약하면, 공급 세대수와 지원자들의 청약가점을 바탕으로
**커트라인(당첨 최저 가점)** 과 **경쟁률**을 계산해 조회할 수 있다.

### 기술 스택 (Spring 대응)

| 항목 | 본 프로젝트 | Spring 대응 |
|---|---|---|
| 언어/런타임 | Python 3.14 | Java |
| 프레임워크 | Django 6 | Spring Boot |
| API 레이어 | Django REST Framework | Spring MVC (`@RestController`) |
| ORM | Django ORM | JPA/Hibernate |
| DB | **PostgreSQL 16** | PostgreSQL |
| DB 드라이버 | psycopg (psycopg3) | JDBC 드라이버 + HikariCP |
| PK 전략 | **UUID** (`uuid4`) | `@GeneratedValue(strategy=UUID)` |
| 마이그레이션 | Django Migrations | Flyway/Liquibase |
| 직렬화(DTO) | DRF Serializer | Jackson + DTO |

### UUID PK 구현 (Django)

모든 모델의 PK는 다음 패턴으로 정의한다. (공통 추상 베이스 모델로 묶어 재사용)

```python
import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
```

> 스프링 비유: JPA의 `@MappedSuperclass` + `@Id @GeneratedValue(strategy=UUID)` 를
> 추상 베이스 클래스로 뽑아둔 것과 동일. 각 엔티티는 이 `BaseModel`을 상속한다.

### 데이터베이스 연결 (`settings.py`)

DB는 **도커 컨테이너로 실행**한다 (`docker-compose.yml`의 `db` 서비스). Django는 로컬에서 돌며 아래 설정으로 접속한다.

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hkhousub",
        "USER": "hkhousub",
        "PASSWORD": "hkhousub",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

> 스프링 비유: `application.yml`의 `spring.datasource.*` 설정과 1:1 대응.
> 자격증명은 `docker-compose.yml`의 `POSTGRES_*` 값과 일치해야 한다.
> 로컬 개발 편의상 하드코딩하지만, 실무에선 환경변수로 분리한다.

---

## 2. 도메인 모델 (ERD)

```
Complex(단지) 1 ──< N Apartment(아파트/주택형) 1 ──< N Application(청약) N >── 1 Member(회원)
```

- 한 **단지**는 여러 **아파트(주택형)** 을 가진다. (1:N)
- 한 **아파트**는 여러 **청약**을 받는다. (1:N)
- 한 **회원**은 여러 **청약**을 넣는다. (1:N)
- `Application`은 `Apartment`와 `Member`를 잇는 조인 성격의 엔티티다.
- **한 회원은 같은 아파트에 중복 청약 불가** → `(apartment, member)` 유니크 제약.

---

## 3. 테이블 명세

### 3.1 `complex` — 단지

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | UUID | PK, default uuid4 | 식별자 |
| name | VARCHAR(100) | NOT NULL | 단지명 (예: "래미안 강남") |
| region | VARCHAR(100) | NOT NULL | 지역 (예: "서울 강남구") |
| created_at | DATETIME | auto | 생성 시각 |

### 3.2 `apartment` — 아파트(주택형)

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | UUID | PK, default uuid4 | 식별자 |
| complex_id | UUID | FK → complex, NOT NULL | 소속 단지 |
| name | VARCHAR(50) | NOT NULL | 주택형 (예: "84A", "59B") |
| area | DECIMAL(6,2) | NULL | 전용면적(㎡) |
| supply_count | INT | NOT NULL, > 0 | **공급 세대수 (커트라인 계산의 N)** |
| price | BIGINT | NULL | 분양가(원) |
| created_at | DATETIME | auto | 생성 시각 |

### 3.3 `member` — 회원

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | UUID | PK, default uuid4 | 식별자 |
| name | VARCHAR(50) | NOT NULL | 회원명 |
| score | INT | NOT NULL, 0~84 | **청약가점** |
| created_at | DATETIME | auto | 생성 시각 |

> 청약가점 만점은 84점 (실제 제도 기준). MVP에서는 단순 정수 필드로만 둔다.

### 3.4 `application` — 청약

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | UUID | PK, default uuid4 | 식별자 |
| apartment_id | UUID | FK → apartment, NOT NULL | 청약 대상 아파트 |
| member_id | UUID | FK → member, NOT NULL | 청약한 회원 |
| score | INT | NOT NULL | 청약 시점의 가점 스냅샷 |
| created_at | DATETIME | auto | 청약 시각 |
| — | — | UNIQUE(apartment_id, member_id) | 중복 청약 방지 |

> `score`를 스냅샷으로 저장하는 이유: 회원의 가점이 나중에 바뀌어도, 그 청약 당시 점수로 커트라인이 계산되어야 하기 때문. (JPA에서 주문 시점 가격을 주문 라인에 복사해두는 것과 같은 패턴)

---

## 4. 비즈니스 로직 — 커트라인 & 경쟁률

아파트의 공급 세대수를 `N`이라 하고, 그 아파트에 들어온 청약 수를 `C`라 할 때:

1. 청약들을 **가점 내림차순**으로 정렬한다. (동점이면 **먼저 청약한 사람**이 앞 — `created_at` 오름차순)
2. **`C ≥ N`** → **커트라인 = N등(정렬 후 N번째) 청약의 가점**, 상태 = `마감`
3. **`C < N`** → 커트라인 없음(`null`), 상태 = `미달`
4. **경쟁률 = C / N** (소수 둘째 자리 반올림)

이 값들은 **DB에 저장하지 않고 조회 시점에 계산**한다. (파생 데이터)

---

## 5. API 명세

- Base URL: `/api/`
- 응답 형식: JSON
- MVP 범위이므로 **인증 없음**.

### 5.1 단지

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/api/complexes/` | 단지 목록 |
| POST | `/api/complexes/` | 단지 등록 |
| GET | `/api/complexes/{id}/` | 단지 상세 (소속 아파트 포함) |

**POST `/api/complexes/` 요청**
```json
{ "name": "래미안 강남", "region": "서울 강남구" }
```

### 5.2 아파트

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/api/apartments/` | 아파트 목록 |
| POST | `/api/apartments/` | 아파트 등록 |
| GET | `/api/apartments/{id}/` | 아파트 상세 |
| GET | **`/api/apartments/{id}/cutline/`** | **커트라인 조회 ★** |

**POST `/api/apartments/` 요청**
```json
{ "complex": "3f9a1c2e-...", "name": "84A", "area": 84.97, "supply_count": 3, "price": 1200000000 }
```
> FK 필드(`complex`)에는 대상의 **UUID 문자열**을 넣는다.

**GET `/api/apartments/{id}/cutline/` 응답 (예)**
```json
{
  "apartment_id": "3f9a1c2e-...",
  "apartment_name": "84A",
  "supply_count": 3,
  "application_count": 5,
  "competition_rate": 1.67,
  "status": "마감",
  "cutline_score": 62
}
```
미달인 경우:
```json
{
  "apartment_id": "7b2d4f10-...",
  "apartment_name": "59B",
  "supply_count": 10,
  "application_count": 4,
  "competition_rate": 0.4,
  "status": "미달",
  "cutline_score": null
}
```

### 5.3 회원

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/api/members/` | 회원 목록 |
| POST | `/api/members/` | 회원 등록 |
| GET | `/api/members/{id}/` | 회원 상세 |

**POST `/api/members/` 요청**
```json
{ "name": "홍길동", "score": 62 }
```

### 5.4 청약

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/api/applications/` | 청약 목록 |
| POST | **`/api/applications/`** | **청약하기 ★** |
| GET | `/api/applications/{id}/` | 청약 상세 |

**POST `/api/applications/` 요청**
```json
{ "apartment": "3f9a1c2e-...", "member": "a1b2c3d4-..." }
```
- `score`는 서버가 회원의 현재 가점을 복사해 자동 저장한다. (요청에 넣지 않음)
- 이미 같은 아파트에 청약한 회원이면 **400 에러** (유니크 제약 위반).

**응답 (예)**
```json
{
  "id": "9c8b7a6d-...",
  "apartment": "3f9a1c2e-...",
  "member": "a1b2c3d4-...",
  "score": 62,
  "created_at": "2026-07-27T01:10:00Z"
}
```

---

## 6. 검증 규칙 (Validation)

| 대상 | 규칙 |
|---|---|
| `member.score` | 0 이상 84 이하 |
| `apartment.supply_count` | 1 이상 |
| 청약 중복 | 같은 `(apartment, member)` 조합 재청약 불가 → 400 |

---

## 7. MVP 범위 밖 (추후 확장)

- 회원 인증/로그인 (Django auth, JWT)
- 청약 기간(오픈/마감 일시) 관리
- 1순위/2순위, 지역 우선공급 등 실제 청약 규칙
- 페이지네이션, 필터링, 정렬 쿼리 파라미터
- 관리자 화면 커스터마이징

---

## 8. 구현 순서 (체크리스트)

- [ ] `subscription` 앱 생성, `INSTALLED_APPS`에 `rest_framework` + `subscription` 등록
- [ ] `models.py` — Complex / Apartment / Member / Application
- [ ] `makemigrations` → `migrate`
- [ ] `serializers.py` — 4개 도메인 + Cutline 응답용
- [ ] `views.py` — ViewSet 4개 + `cutline` 커스텀 액션
- [ ] `urls.py` — DRF Router 등록, `config/urls.py`에 include
- [ ] `admin.py` 등록 → 관리자 화면으로 시드 데이터 입력
- [ ] API 테스트 (커트라인/청약 시나리오 검증)
