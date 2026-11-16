"""인천공항 오늘 출발 여객편을 받아 travel/dashboards/icn-airlines/data/flights.json 으로 쓴다.

키는 저장소 Secrets 의 AIRPLANE 에서 환경변수 ICN_KEY 로만 받는다. 파일·로그에 키를 남기지 않는다.
API: 공공데이터포털 '인천국제공항공사_여객편 운항현황(다국어)'
     https://apis.data.go.kr/B551177/StatusOfPassengerFlightsOdp
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
BASE = "https://apis.data.go.kr/B551177/StatusOfPassengerFlightsOdp"
OPS = ["getPassengerDeparturesOdp"]
OUT = "travel/dashboards/icn-airlines/data/flights.json"
TERM = {"P01": "T1", "P02": "T1", "P03": "T2"}   # P02 = 탑승동(T1 쪽 셔틀)


def call(op, key, page):
    q = {"serviceKey": key, "type": "json", "lang": "K", "numOfRows": 1000, "pageNo": page}
    url = f"{BASE}/{op}?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read().decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except ValueError:
        # 키 오류 등은 XML 로 온다. 키가 섞이지 않게 앞부분만 보여 준다.
        raise SystemExit(f"{op}: JSON 아님 — {raw[:200].replace(key, '***')}")


def items(j):
    body = (j.get("response") or {}).get("body") or {}
    it = body.get("items") or []
    if isinstance(it, dict):
        it = it.get("item") or []
    if isinstance(it, dict):
        it = [it]
    return it, int(body.get("totalCount") or 0)


def main():
    key = os.environ.get("ICN_KEY", "").strip()
    if not key:
        sys.exit("ICN_KEY 없음 — 저장소 Secrets 에 AIRPLANE 을 넣어 주세요")
    rows, last = [], None
    for op in OPS:
        try:
            page, rows = 1, []
            while True:
                it, total = items(call(op, key, page))
                rows += it
                if not it or len(rows) >= total or page >= 10:
                    break
                page += 1
            break
        except Exception as e:   # noqa: BLE001
            last = e
    if not rows:
        sys.exit(f"응답 없음: {last}")

    out, seen = [], set()
    for r in rows:
        if str(r.get("codeshare") or "").lower() == "slave":
            continue                       # 공동운항 편은 대표 편만
        fid = str(r.get("flightId") or "").strip()
        t = str(r.get("estimatedDateTime") or r.get("scheduleDateTime") or "")
        if not fid or (fid, t) in seen:
            continue
        seen.add((fid, t))
        out.append({
            "airline": r.get("airline") or "",
            "flight": fid,
            "dest": r.get("airport") or "",
            "time": t[-4:],
            "terminal": TERM.get(str(r.get("terminalId") or ""), str(r.get("terminalId") or "")),
            "gate": str(r.get("gatenumber") or ""),
            "status": r.get("remark") or "",
        })
    out.sort(key=lambda f: f["time"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now(KST).isoformat(timespec="seconds"), "flights": out},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"출발 {len(out)}편 저장 (원본 {len(rows)}건)")


if __name__ == "__main__":
    main()
