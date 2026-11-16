# 인천공항 항공사별 현황 대시보드

`index.html` 하나로 동작한다. 1단계는 항공사 목록·터미널·카운터·공식 링크, 2단계는 `data/flights.json` 이 생기면 "실시간 현황" 영역이 자동으로 나타난다(없으면 숨김).

## 1단계 데이터 출처 (기준일 2026-11-16)

- 터미널: 인천국제공항 공식 홈페이지 취항정보 https://www.airport.kr/ap_ko/881/subview.do (전월 여객·화물 정기편 기준, 화물 전용 항공사는 뺐다)
- 카운터: 체크인 카운터 안내 https://www.airport.kr/ap_ko/894/subview.do — 대한항공·아시아나항공만 구역이 나와 있다.
- 진에어·에어부산·에어서울(T2 서편 D·E), 트리니티항공 A·B, 에어프레미아 C, 파라타항공 B 는 뉴시스 2025-12-15 보도(https://www.newsis.com/view/NISX20251215_0003442075) 기준이라 화면에 "보도 기준" 표시를 붙였다.
- 나머지 항공사 카운터는 "확인 필요".
- 공항 실시간 현황: 출발편 https://www.airport.kr/ap_ko/869/subview.do · 도착편 https://www.airport.kr/ap_ko/872/subview.do

## 2단계: data/flights.json 형식

```json
{
  "updated": "2026-11-16T09:30:00+09:00",
  "flights": [
    {"airline": "대한항공", "flight": "KE123", "dest": "도쿄/나리타", "time": "1035", "terminal": "T2", "gate": "250", "status": "지연"}
  ]
}
```

- `updated`: ISO 8601 시각(파일을 만든 시각)
- `flights[]`: 오늘 인천 **출발** 여객편
  - `airline`: 항공사 한글명 (API `airline`)
  - `flight`: 편명 (API `flightId`) — 앞 2글자를 IATA 코드로 보고 항공사와 맞춘다
  - `dest`: 도착 공항 이름 (API `airport`)
  - `time`: 예정 시각 `HHMM` 또는 `YYYYMMDDHHMM` (API `scheduleDateTime`; 변경 시각을 쓰려면 `estimatedDateTime`)
  - `terminal`: `T1`/`T2` 로 바꿔 넣는다 (API `terminalId` — 코드값과 T1/T2 대응은 첫 응답에서 확인해 매핑)
  - `gate`: 탑승구 (API `gatenumber`)
  - `status`: 현황 (API `remark` — 출발, 결항, 지연, 탑승중 등). 화면은 "지연"·"결항" 글자를 세어 지연·결항 편수를 낸다.
- 화면은 `status` 가 결항이 아닌 편 가운데 지금 이후 출발 8편을 보여 준다. 항공사를 누르면 그 항공사만.

## 2단계: 공공데이터포털 API

- 이름: **인천국제공항공사_여객편 운항현황(다국어)**
- 신청: https://www.data.go.kr/data/15095093/openapi.do (활용신청 → 마이페이지에서 일반 인증키 발급)
- 서비스 URL: `https://apis.data.go.kr/B551177/StatusOfPassengerFlightsOdp`
- 도착 오퍼레이션: `getPassengerArrivalsOdp` (포털 상세 페이지에서 확인)
- 출발 오퍼레이션: `getPassengerDeparturesOdp` — 포털 화면에 이름이 따로 안 나와 도착 이름 규칙으로 적은 것. **활용신청 후 상세 명세에서 꼭 확인**.
- 요청 변수: `serviceKey`(필수), `from_time`·`to_time`(HHMM), `airport`(IATA), `flight_id`, `airline`(IATA), `lang`, `type`(xml/json)
- 응답 필드(도착 기준, 포털 표기): `typeOfFlight`, `airline`, `flightId`, `scheduleDateTime`, `estimatedDateTime`, `airport`, `gatenumber`, `carousel`, `cityCode`, `exitnumber`, `remark`, `airportCode`, `terminalId`, `elapsetime`, `codeshare`, `masterflightid` (+ 경유지 필드)
- 갱신주기: 실시간
- 비슷한 대안: 인천국제공항공사_여객기 운항 현황 상세 조회 서비스 https://www.data.go.kr/data/15112968/openapi.do (`StatusOfPassengerFlightsDeOdp`, 도착 `getPassengerArrivalsDeOdp`, 날짜 `searchday` 지원)

## GitHub Actions 로 채울 때 메모

- 인증키는 저장소 Secrets(예: `ICN_API_KEY`)에만 넣고, 코드·파일에 쓰지 않는다.
- 하루 호출 한도가 있으니 10~30분 간격이면 충분하다.
- 코드셰어로 같은 편이 여러 번 올 수 있으니 `codeshare`·`masterflightid` 로 대표 편만 남긴다(값 형식은 첫 응답에서 확인).
- 결과 파일 경로: `travel/dashboards/icn-airlines/data/flights.json`
