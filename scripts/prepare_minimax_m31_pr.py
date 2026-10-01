"""One-shot preparation for the contributor's M3.1 branch; removed before PR."""
from pathlib import Path
import ast
import json

ROOT = Path(__file__).resolve().parent.parent


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Reviewed anchor changed; stop rather than overwrite unrelated changes")
    return text.replace(old, new, 1)


def main():
    updates = {}
    p = ROOT / "scripts/build_adopted.py"
    text = p.read_text(encoding="utf-8")
    old = "    rows = [sub_row(*s) for s in SUBS if (s[0], s[4]) not in EXCLUDED_SUBSCRIPTIONS]\n"
    new = "    from minimax_m31_rows import subscription_specs as minimax_m31_specs\n" + old + "    rows.extend(sub_row(*s) for s in minimax_m31_specs(CONVENTIONS))\n"
    updates[p] = replace_once(text, old, new)
    p = ROOT / "scripts/compute.py"
    updates[p] = replace_once(p.read_text(encoding="utf-8"), "DISPLAY = {\n", "DISPLAY = {\n    \"minimax-m3.1-flash-preview\": \"MiniMax M3.1 Flash Preview\",\n")
    p = ROOT / "CONVENTIONS.md"
    rule = ("\n- **MiniMax M Plan × M3.1 Flash Preview（2026-10-01 暂估例外提案）**：投稿者确认国区Go，独立M3.1计价比例未核实，暂提raw/`measured`未折算点供维护者审阅，不改变其他有分项样本的归一规则。起点小时计数为零、无其他共享池消耗未单独确认；Go月付medium，年付/跨档low。年付按实际年费/12参与比较并标整年预付；不是一次发放全年额度。维护者不接受时只保留research；取得价格比例后重算。\n")
    updates[p] = replace_once(p.read_text(encoding="utf-8"), "## 4. 各渠道现行口径\n", "## 4. 各渠道现行口径\n" + rule)
    p = ROOT / "DECISIONS.md"
    updates[p] = p.read_text(encoding="utf-8") + ("\n\n## 2026-10-01 · MiniMax M Plan 国区 M3.1 Flash Preview 暂估投稿\n\n"
        "- 投稿者确认实测为Go并授权提交。新增Go/Explore/Build月付与年付共六点，不替换历史Token Plan或M3。\n"
        "- 月付¥49/119/469；年付¥490/1190/4690，比较月费保留年费/12完整精度；国区倍率1:3:12。Explore截图划线1490与119×12=1428冲突保留，不据划线价倒推月付。\n"
        "- 原始样本23,970,451 tok，周4%→10%，5h41%→100%。Go raw月估计15.98030067亿；按sub_row现有精度生成15.980/47.941/191.764亿。中末差分12,201,679/3%×4=16.26890533亿仅对照。\n"
        "- 起点12:01但用量桶从12:00起，起点计数零及独占共享池仍是假设。周取整敏感性13.6974~19.1764亿不是统计置信区间；5h不是完整0%→100%窗。\n"
        "- 显式raw例外交维护者审阅：M3.1价格比例未核实，不能借用M3；workload=measured并注明未折算。月付Go medium，年付和跨档low；3×/12×周池及年付同额均为推算。\n"
        "- 不借M3分数，不造API价。证据JSON含六张截图转录及原始SHA-256；二进制原图保留于投稿者审阅包，未随本次文本提交上传，不宣称仓库已有原图。\n"
        "- 证据：`data/research/minimax-m31-flash-preview-cn-round1-2026-10-01.json`。\n")
    p = ROOT / "data/conventions.json"
    text = p.read_text(encoding="utf-8")
    before = json.loads(text)["updatedAt"]
    if before > "2026-10-01":
        raise ValueError("Upstream snapshot newer than the reviewed submission")
    updates[p] = replace_once(text, f'"updatedAt": "{before}"', '"updatedAt": "2026-10-01"')
    for path, text in updates.items():
        if path.suffix == ".py":
            ast.parse(text)
        elif path.suffix == ".json":
            json.loads(text)
    for path, text in updates.items():
        path.write_text(text, encoding="utf-8")
    print("Applied reviewed adoption hooks, display label and explicit provisional rule.")


if __name__ == "__main__":
    main()
