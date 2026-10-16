"""Conservative slide matching. Visible-window text is never written to disk."""
import math
import re
from collections import Counter

STOP = set('the and for with this that from are was have has into your you slide page pdf of to in is a an on by as or it be at not'.split())


def tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]{2,}", text.casefold()) if word not in STOP}


def match_slide(text: str, pages: list[tuple[int, str]]) -> dict:
    visible = tokens(text)
    indexed = [(number, tokens(content)) for number, content in pages]
    frequency = Counter(word for _, words in indexed for word in words)
    weights = {word: 1 + math.log((len(indexed) + 1) / (count + 1)) for word, count in frequency.items()}
    visible_weight = sum(weights[word] for word in visible if word in weights)
    ranked = []
    complete = []
    for number, words in indexed:
        shared = words & visible
        shared_weight = sum(weights[word] for word in shared)
        page_weight = sum(weights[word] for word in words)
        coverage = shared_weight / max(1, page_weight)
        # Coverage alone incorrectly ties a longer slide with a shorter slide
        # whose content it contains. Also account for distinctive extra text.
        score = 2 * shared_weight / max(1, page_weight + visible_weight)
        if coverage >= .88 and len(shared) >= 6:
            complete.append(words)
        # A common title or footer alone cannot identify a slide.
        ranked.append((score if len(shared) >= 6 and coverage >= .68 else 0, number, len(shared)))
    # Two substantially complete, distinct slides may share a viewport. Do not
    # select the longer one simply because it supplies most of the words.
    for index, first in enumerate(complete):
        for second in complete[index + 1:]:
            if len((first - second) & visible) >= 4 and len((second - first) & visible) >= 4:
                return {"page": None, "status": "ambiguous"}
    ranked.sort(reverse=True)
    if not ranked or ranked[0][0] < .68:
        return {"page": None, "status": "unknown"}
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < .16:
        return {"page": None, "status": "ambiguous"}
    return {"page": ranked[0][1], "status": "matched"}
