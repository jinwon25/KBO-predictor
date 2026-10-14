import sqlite3
import unittest

from demo.operations_audit import build_mart, summarize, synthetic_inputs, timestamp, quantiles

class OperationsAuditTests(unittest.TestCase):
    def test_schedule_left_join_and_latest_timely_success(self):
        con = build_mart(*synthetic_inputs())
        self.addCleanup(con.close)
        rows = {r["game_key"]: dict(r) for r in con.execute("SELECT * FROM game_audit")}
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows["A"]["event_id"], "a2")
        self.assertEqual(rows["A"]["probability_matches"], 1)
        self.assertEqual(rows["B"]["receipt_evidence"], "unconfirmed")
        self.assertEqual(rows["C"]["receipt_evidence"], "unconfirmed")
        self.assertEqual(rows["D"]["receipt_evidence"], "late_success_only")
        report = summarize(con)
        self.assertEqual(report["retained_predictions"], 3)
        self.assertEqual(report["confirmed_timely"], 1)
        self.assertAlmostEqual(report["cutoff_margin_minutes"]["min"], 12)
        self.assertEqual(report["generated_to_receipt_seconds"]["p50"], 120)

    def test_timezone_equivalence_and_exact_cutoff(self):
        schedule, predictions, receipts = synthetic_inputs()
        receipts[1]["received_at"] = "2030-06-01T09:15:00Z"
        con = build_mart(schedule, predictions, receipts)
        self.addCleanup(con.close)
        self.assertEqual(summarize(con)["cutoff_margin_minutes"]["min"], 0)
        self.assertEqual(timestamp("2030-06-01T18:15:00+09:00"),
                         timestamp("2030-06-01T09:15:00Z"))
        with self.assertRaises(ValueError):
            timestamp("2030-06-01T18:15:00")

    def test_duplicate_keys_and_orphans_fail_instead_of_multiplying_rows(self):
        s, p, r = synthetic_inputs()
        for inputs in [(s+s[:1],p,r), (s,p+p[:1],r), (s,p,r+r[:1]),
                       (s,p+[dict(p[0],game_key="orphan")],r),
                       (s,p,r+[dict(r[0],event_id="new",game_key="orphan")])]:
            with self.subTest(inputs=inputs), self.assertRaises(sqlite3.IntegrityError):
                build_mart(*inputs)

    def test_invalid_probabilities_are_not_coerced(self):
        s,p,r = synthetic_inputs()
        for value in [float("nan"), float("inf"), -.1, 1.1, True, "0.5"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_mart(s, [dict(p[0], probability_home=value)], r)

    def test_missing_and_inverted_times_are_not_zero_duration(self):
        s,p,r = synthetic_inputs()
        p[0]["generated_at"] = "2030-06-01T18:04:00+09:00"
        p[1]["generated_at"] = None
        con = build_mart(s,p,r)
        self.addCleanup(con.close)
        report = summarize(con)
        self.assertEqual(report["generated_after_selected_receipt"], 1)
        self.assertEqual(report["generated_timestamp_missing"], 1)
        self.assertEqual(report["generated_to_receipt_seconds"]["n"], 0)
        self.assertIsNone(report["generated_to_receipt_seconds"]["p50"])

    def test_probability_mismatch_excluded_from_elapsed_pairs(self):
        s,p,r = synthetic_inputs()
        p[0]["probability_home"] = .7
        con = build_mart(s,p,r)
        self.addCleanup(con.close)
        report = summarize(con)
        self.assertEqual(report["receipt_probability_mismatches"], 1)
        self.assertEqual(report["generated_to_receipt_seconds"]["n"], 0)

    def test_successful_timestamp_ties_are_visible(self):
        s,p,r = synthetic_inputs()
        r.append(dict(r[1],event_id="a2b",probability_home=.9))
        con = build_mart(s,p,r)
        self.addCleanup(con.close)
        self.assertEqual(summarize(con)["successful_timestamp_tie_groups"], 1)

    def test_missing_and_blank_identifiers_are_rejected(self):
        for value in [None, "", "   ", "\t", 123, True]:
            for group, field in [(0,"game_key"), (1,"game_key"),
                                 (2,"game_key"), (2,"event_id")]:
                inputs = synthetic_inputs()
                inputs[group][0][field] = value
                with self.subTest(value=value,group=group,field=field):
                    with self.assertRaises(ValueError):
                        build_mart(*inputs)

    def test_probability_matching_uses_submission_rounding(self):
        for saved, received, matches in [
            (.6001,.6,0), (.60004,.6,1), (.60005,.6,0),
            (.59995,.6,1), (.50005,.5,0), (.500049,.5,1),
            (0,0,1), (1,1,1)
        ]:
            s,p,r = synthetic_inputs()
            p[0]["probability_home"] = saved
            r[1]["probability_home"] = received
            con = build_mart(s,p,r)
            try:
                with self.subTest(saved=saved,received=received):
                    row = con.execute(
                        "SELECT probability_matches FROM game_audit WHERE game_key='A'"
                    ).fetchone()
                    self.assertEqual(row[0],matches)
                    self.assertEqual(summarize(con)["generated_to_receipt_seconds"]["n"], matches)
            finally:
                con.close()

    def test_backed_up_mart_keeps_probability_comparison(self):
        s,p,r = synthetic_inputs()
        p[0]["probability_home"] = .6001
        source = build_mart(s,p,r)
        self.addCleanup(source.close)
        copy = sqlite3.connect(":memory:")
        self.addCleanup(copy.close)
        source.backup(copy)
        self.assertEqual(copy.execute(
            "SELECT probability_matches FROM game_audit WHERE game_key='A'"
        ).fetchone()[0],0)

    def test_empty_mart_and_quantiles(self):
        con = build_mart([],[],[])
        self.addCleanup(con.close)
        self.assertEqual(summarize(con)["schedule_rows"],0)
        self.assertIsNone(quantiles([])["min"])
        self.assertEqual(quantiles([1,2,3,4])["p50"],2.5)
        self.assertEqual(quantiles([7])["p95"],7)

if __name__ == "__main__":
    unittest.main()
