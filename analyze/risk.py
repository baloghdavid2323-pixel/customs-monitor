import re
from typing import Dict, Tuple

def score_item(text: str, rules: Dict) -> Tuple[str, bool, bool]:
    text_lc = text.lower() if text else ""
    risk = "low"
    for level in ["high", "medium", "low"]:
        patterns = rules.get(level, {}).get("any", [])
        for p in patterns:
            if re.search(re.escape(p.lower()), text_lc):
                risk = level
                break
        if risk == level:
            break

    direct = any(tag.lower() in text_lc for tag in rules.get("impact_tags", {}).get("direct", []))
    indirect = any(tag.lower() in text_lc for tag in rules.get("impact_tags", {}).get("indirect", []))

    return risk, direct, indirect
