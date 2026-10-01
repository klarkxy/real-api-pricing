"""Verify arithmetic, six adopted rows, annual precision and provisional labels."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from minimax_m31_rows import EVIDENCE, MODEL, subscription_specs


def main() -> None:
    conventions = json.loads((ROOT / "data/conventions.json").read_text(encoding="utf-8"))
    doc = json.loads((ROOT / "data/research" / EVIDENCE).read_text(encoding="utf-8"))
    usage = doc["calculations"]["usage"]
    assert sum(usage["endBucketCumulative"].values()) == usage["endBucketTotal"] == 23970451
    delta = {k: v - usage["midBucketCumulative"][k] for k, v in usage["endBucketCumulative"].items()}
    assert delta == usage["midToEndDelta"] and sum(delta.values()) == 12201679
    assert len(doc["originalEvidence"]["screenshots"]) == 6
    for image in doc["originalEvidence"]["screenshots"]:
        assert len(image["sha256"]) == 64 and int(image["sha256"], 16) >= 0
    with (ROOT / "data/adopted.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["served_model"] == MODEL]
    by_id = {r["plan_id"]: r for r in rows}
    assert len(rows) == len(by_id) == 6
    for pid, _, price, currency, _, yi, confidence, *_ in subscription_specs(conventions):
        row = by_id[pid]
        tokens = round(round(yi, 3) * 100000000)
        expected = price / conventions["usdPerCny"] / tokens * 1000000
        assert int(row["monthly_tokens"]) == tokens, pid
        assert row["currency"] == currency and row["confidence"] == confidence, pid
        assert row["workload"] == "measured", pid
        assert "未折算" in row["decision_note"] and "暂估" in row["decision_note"], pid
        assert math.isclose(float(row["price"]), price, rel_tol=1e-12), pid
        assert math.isclose(float(row["real_usd_per_mtok"]), expected, rel_tol=1e-7), pid
        if pid.endswith("_annual"):
            monthly = by_id[pid.removesuffix("_annual")]
            assert row["monthly_tokens"] == monthly["monthly_tokens"], pid
            assert "整年预付" in row["decision_note"], pid
            assert math.isclose(price / float(monthly["price"]), 5 / 6, rel_tol=1e-12), pid
    print("PASS: six M3.1 rows, arithmetic, annual precision, confidence and raw labels. Original image bytes are not in this checkout.")


if __name__ == "__main__":
    main()
