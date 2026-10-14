"""일정 중심 SQL 대조. 기본 실행은 독립 합성 자료이며 네트워크를 쓰지 않는다."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from demo.scoring import normalize_probability
import json
import math
import sqlite3

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE schedule (
 game_key TEXT NOT NULL PRIMARY KEY, start_at REAL NOT NULL, cutoff_at REAL NOT NULL,
 outcome TEXT NOT NULL CHECK(outcome IN ('home','away','draw','cancelled','pending')),
 eligible INTEGER NOT NULL CHECK(eligible IN (0,1))
);
CREATE TABLE retained_prediction (
 game_key TEXT NOT NULL PRIMARY KEY REFERENCES schedule(game_key),
 probability_home REAL NOT NULL CHECK(probability_home BETWEEN 0 AND 1),
 probability_units INTEGER NOT NULL CHECK(probability_units BETWEEN 0 AND 10000),
 generated_at REAL
);
CREATE TABLE receipt_event (
 event_id TEXT NOT NULL PRIMARY KEY, game_key TEXT NOT NULL REFERENCES schedule(game_key),
 received_at REAL NOT NULL, succeeded INTEGER NOT NULL CHECK(succeeded IN (0,1)),
 probability_home REAL NOT NULL CHECK(probability_home BETWEEN 0 AND 1),
 probability_units INTEGER NOT NULL CHECK(probability_units BETWEEN 0 AND 10000)
);
CREATE VIEW game_audit AS
WITH ranked AS (
 SELECT r.*, ROW_NUMBER() OVER (
  PARTITION BY r.game_key ORDER BY r.received_at DESC, r.event_id DESC
 ) AS ordinal
 FROM receipt_event r JOIN schedule s USING(game_key)
 WHERE r.succeeded=1 AND r.received_at<=s.cutoff_at
)
SELECT s.*, p.probability_home, p.generated_at,
 r.event_id, r.received_at, r.probability_home AS received_probability,
 CASE WHEN r.event_id IS NOT NULL THEN 'confirmed_timely'
      WHEN EXISTS(SELECT 1 FROM receipt_event e WHERE e.game_key=s.game_key
                  AND e.succeeded=1) THEN 'late_success_only'
      ELSE 'unconfirmed' END AS receipt_evidence,
 CASE WHEN r.event_id IS NOT NULL AND p.game_key IS NOT NULL
      THEN r.probability_units=p.probability_units
      ELSE NULL END AS probability_matches
FROM schedule s LEFT JOIN retained_prediction p USING(game_key)
LEFT JOIN ranked r ON r.game_key=s.game_key AND r.ordinal=1;
"""

def timestamp(value):
    """Require an explicit offset; compare instants rather than local strings."""
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO string with timezone")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timezone required")
    return dt.timestamp()

def probability(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("probability must be a finite number in [0, 1]")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("probability must be a finite number in [0, 1]")
    return value

def identifier(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("identifier must be a non-empty string")
    return value

def submission_units(value):
    """Integer hundredths of a percentage point, using the shared demo rule."""
    return int(normalize_probability(Decimal(str(value))*100)*100)

def build_mart(schedule, predictions, receipts):
    """One schedule version and one retained prediction per game, all supplied events.

    This does not reconstruct missing historical runs or certify API acceptance.
    Event IDs break timestamp ties deterministically; ties are reported for review.
    """
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    try:
        for s in schedule:
            start = timestamp(s["start_at"])
            cutoff = timestamp(s["cutoff_at"])
            if cutoff >= start:
                raise ValueError("cutoff must precede game start")
            con.execute("INSERT INTO schedule VALUES (?,?,?,?,?)",
                        (identifier(s["game_key"]), start, cutoff, s["outcome"], s["eligible"]))
        for p in predictions:
            value = probability(p["probability_home"])
            con.execute("INSERT INTO retained_prediction VALUES (?,?,?,?)",
                        (identifier(p["game_key"]), value, submission_units(value),
                         timestamp(p["generated_at"]) if p.get("generated_at") else None))
        for r in receipts:
            value = probability(r["probability_home"])
            con.execute("INSERT INTO receipt_event VALUES (?,?,?,?,?,?)",
                        (identifier(r["event_id"]), identifier(r["game_key"]),
                         timestamp(r["received_at"]), r["succeeded"], value,
                         submission_units(value)))
        con.commit()
    except Exception:
        con.close()
        raise
    return con

def quantiles(values):
    """Linear interpolation; never infer zero duration from a missing timestamp."""
    values = sorted(values)
    if not values:
        return {"n": 0, "min": None, "p50": None, "p95": None, "max": None}
    def q(frac):
        pos = (len(values)-1)*frac
        lo = math.floor(pos)
        hi = math.ceil(pos)
        return values[lo]+(values[hi]-values[lo])*(pos-lo)
    return {"n": len(values), "min": values[0], "p50": q(.5),
            "p95": q(.95), "max": values[-1]}

def summarize(con):
    rows = [dict(r) for r in con.execute("SELECT * FROM game_audit ORDER BY game_key")]
    confirmed = [r for r in rows if r["received_at"] is not None]
    paired = [r for r in confirmed if r["generated_at"] is not None]
    invalid = [r for r in paired if r["generated_at"] > r["received_at"]]
    valid = [r for r in paired if r["generated_at"] <= r["received_at"]
             and r["probability_matches"] == 1]
    ties = con.execute("""
      SELECT COUNT(*) FROM (
       SELECT game_key,received_at FROM receipt_event WHERE succeeded=1
       GROUP BY game_key,received_at HAVING COUNT(*)>1
      )""").fetchone()[0]
    return {
        "schedule_rows": len(rows),
        "eligible_rows": sum(r["eligible"] for r in rows),
        "retained_predictions": sum(r["probability_home"] is not None for r in rows),
        "confirmed_timely": len(confirmed),
        "unconfirmed": sum(r["receipt_evidence"] == "unconfirmed" for r in rows),
        "late_success_only": sum(r["receipt_evidence"] == "late_success_only" for r in rows),
        "receipt_probability_mismatches": sum(r["probability_matches"] == 0 for r in confirmed),
        "generated_timestamp_missing": sum(r["probability_home"] is not None
                                           and r["generated_at"] is None for r in rows),
        "prediction_after_start": sum(r["generated_at"] is not None
                                      and r["generated_at"] >= r["start_at"] for r in rows),
        "generated_after_selected_receipt": len(invalid),
        "successful_timestamp_tie_groups": ties,
        "receipt_lead_minutes": quantiles([(r["start_at"]-r["received_at"])/60 for r in confirmed]),
        "cutoff_margin_minutes": quantiles([(r["cutoff_at"]-r["received_at"])/60 for r in confirmed]),
        "generated_to_receipt_seconds": quantiles([r["received_at"]-r["generated_at"] for r in valid]),
    }

def synthetic_inputs():
    start = datetime(2030, 6, 1, 18, 30, tzinfo=timezone(timedelta(hours=9)))
    schedule, predictions, receipts = [], [], []
    for key, outcome in [("A","home"), ("B","away"), ("C","draw"), ("D","home")]:
        schedule.append(dict(game_key=key, start_at=start.isoformat(),
                             cutoff_at=(start-timedelta(minutes=15)).isoformat(),
                             outcome=outcome, eligible=outcome in ("home","away")))
    for key, p, lead in [("A", .6, 29), ("B", .4, 28), ("D", .7, 20)]:
        predictions.append(dict(game_key=key, probability_home=p,
                                generated_at=(start-timedelta(minutes=lead)).isoformat()))
    for event, key, p, lead, success in [
        ("a1","A",.55,28,1), ("a2","A",.6,27,1), ("a3","A",.8,14,0),
        ("b1","B",.4,27,0), ("d1","D",.7,14,1)
    ]:
        receipts.append(dict(event_id=event, game_key=key, probability_home=p,
                             received_at=(start-timedelta(minutes=lead)).isoformat(),
                             succeeded=success))
    return schedule, predictions, receipts

def main():
    con = build_mart(*synthetic_inputs())
    try:
        print(json.dumps({"scope": "독립 합성 4경기; 실제 운영 성과 아님",
                          "summary": summarize(con)}, ensure_ascii=False, indent=2))
    finally:
        con.close()

if __name__ == "__main__":
    main()
