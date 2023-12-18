# 프로젝트 설명
자본이 있는 고객이 자신의 원화 자본을 토대로 포트폴리오 구성을 요청하고, 관리자는 해당 요청에 대해 자체적인 포트폴리오를 구성하여 고객에게 전달한다.
고객이 해당 전달받은 포트폴리오 구성을 확인하고 승인한다면 주식 구매가 일어나며 고객의 원화 잔고가 줄어들게 된다.

# 테스트 도구
- Postman : Postman을 사용하는데에 있어 POST Method 일 때, Header에 Key : X-CSRFToken, Value : {{csrftoken}}을 추가해주셔야합니다.

# 사전 작업
1. 가상환경 구축
2. db 구축 : db 관련 세팅을 따로 환경 변수로 분리해야하지만 기능 구현 과제라고 생각하여 값을 아예 settings.py에 넣어뒀습니다. 따라서 해당 값에 맞춰서 디비를 세팅해주셔야 합니다.
3. project level에서 requirement.txt install

# 디비 적용
python manage.py migrate

# 기본 데이터 추가
python manage.py loaddata stock_initial_data.json

# 어드민 계정 추가
python manage.py createsuperuser

어드민 페이지 접속 : /admin

# API
## 회원가입
POST: /accounts/register/


```json
{
    "username": {{닉네임}},
    "password": {{비밀번호}}
}

```

## 로그인
POST: /accounts/login/
```json
{
    "username": {{닉네임}},
    "password": {{비밀번호}}
}

```

## 로그아웃
GET: /accounts/logout

## 잔액 조회
GET: /portfolio/balance

## 잔액 수정
POST: /portfolio
```json
{
    "balance_type": {{잔액 수정 타입}} -> "DEPOSIT" or "WITHDRAW",
    "amount": {{금액}}
}
```

## 현재 주식 조회
GET: /portfolio/stock/

## 주식 추가
POST: /portfolio/stock/
```json
{
     "code": {{주식 코드}},
     "name": {{주식 이름}},
     "price": {{한 주당 가격}}
}

```

## 주식 가격 수정
PUT: /portfolio/stock/<pk>
```json
{
    "price": {{수정할 가격}},
}
```

## 주식 삭제
DELETE: /portfolio/stock/<pk>

## 포트폴리오 확인
GET: /portfolio

## 포트폴리오 자문 전달
POST: /portfolio
```json
{
     "stock_data": {
        "{{종목코드}}": {{수량}}
         ...
    },
    "request_id": {{자문요청 객체 아이디}},
}
```

## 자문 요청
POST /portfolio/request
```json
{
    "request_type": {{자문 타입}} -> "HIGH_RISK" or "STABLE"
}
```

## 자문 목록 확인
GET: /portfolio/request

## 자문 승인/거절
PUT: /portfolio/request
```json
{
    "request_id": {{자문 요청 객체 아이디}}.
    "approval_type": {{자문 제의 수락 여부}} -> "APPROVE" or "REJECT"
}
```
