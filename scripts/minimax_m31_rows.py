"""Contributor-proposed CN M Plan rows: raw estimates, not standardized prices."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

EVIDENCE = "minimax-m31-flash-preview-cn-round1-2026-10-01.json"
MODEL = "minimax-m3.1-flash-preview"


def subscription_specs(conventions: dict) -> list[tuple]:
    root = Path(__file__).resolve().parent.parent
    doc = json.loads((root / "data/research" / EVIDENCE).read_text(encoding="utf-8"))
    if doc["measurement"]["accountPlan"] != "Go":
        raise ValueError("Expected the contributor-confirmed Go baseline")
    start, _, end = doc["measurement"]["checkpoints"]
    delta = Decimal(end["weeklyUsedPercent"] - start["weeklyUsedPercent"]) / 100
    total = sum(doc["calculations"]["usage"]["endBucketCumulative"].values())
    if delta <= 0 or total != 23970451:
        raise ValueError("Unexpected sample; re-review before adoption")
    monthly_yi = Decimal(total) / delta * Decimal(str(conventions["monthWeeks"])) / 100000000
    source = ("https://platform.minimax.cn/docs/m-plan/faq；"
              "https://platform.minimax.cn/docs/m-plan/intro；" + EVIDENCE + "；投稿者确认Go")
    common = (
        "未折算、暂估：M3.1独立计价比例未核实，不借用M3价；临时raw例外交维护者审阅。"
        "Go小时累计23,970,451 tok对应周4%→10%，5h41%→100%，并非完整5h窗。"
        "12:01起点的小时计数未截图；假设12:00至起点用量为0、期间无其他共享池消耗，两项未单独确认。"
        "周整数取整敏感性13.6974~19.1764亿/月(4周)，非统计置信区间；"
        "中末差分12,201,679 tok/3pp=16.2689亿/月，仅对照。"
        "全口径缓存/输入/输出95.1823%/3.4854%/1.3323%；面板96.5%为输入缓存命中率。"
        "同负载、饱和使用估算，非官方固定token额度。"
    )
    rows = []
    for plan in doc["calculations"]["prices"]:
        tier, mult = plan["plan"], plan["usageRelativeToGo"]
        for annual in (False, True):
            price = Decimal(plan["annualCny"]) / 12 if annual else Decimal(plan["monthlyCny"])
            pid = f"minimax_m_plan_{tier.lower()}_cn" + ("_annual" if annual else "")
            label = f"MiniMax M Plan {tier} (CN{' Annual' if annual else ''})"
            note = common
            if mult != 1:
                note += f"Go×{mult}跨档外推，假设官方倍率适用于周池，非本档独立实测。"
            if annual:
                note += (f"年付¥{plan['annualCny']}，月比较费=年费/12，需整年预付，不是按月售价；"
                         "假设同档年付/月付周池相同，并非一次发放全年token。")
            else:
                note += f"常规月付¥{plan['monthlyCny']}由年付实价÷10及官方FAQ还原，不含首月促销。"
            if tier == "Explore":
                note += "截图年付划线价1490与119×12=1428不符，保留冲突，不据此倒推月付。"
            conf = "medium" if tier == "Go" and not annual else "low"
            rows.append((pid, label, float(price), "CNY", MODEL, float(monthly_yi * mult),
                         conf, source, note, "full"))
    if len(rows) != 6 or len({r[0] for r in rows}) != 6:
        raise ValueError("Expected six distinct subscription rows")
    return rows
