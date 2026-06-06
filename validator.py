"""
Old English validator — checks model output against the Bosworth-Toller lexicon.
"""

import re
from oe_lexicon import OELexicon, _norm

WORD_RE = re.compile(r"[A-Za-zþðæœāēīōūȳǣǽ']+")

# High-frequency West Saxon function words the stemmer sometimes mangles
_ALWAYS_OK = {_norm(w) for w in [
    "se","seo","þæt","þe","þa","þam","þǣm","þone","þære","þæs","þy",
    "ic","þu","he","heo","hit","we","ge","hi","hie","man",
    "min","þin","his","hire","ure","eower","hyra","heora",
    "and","ac","oþþe","ne","na","no","gif","hwæt","hwær",
    "to","of","on","in","æt","for","mid","be","ymbe","ofer",
    "is","ys","wæs","bið","beoþ","sind","sindon","wæron",
    "eom","eart","earton","earon",
    "þær","her","nu","þonne","swa","eft","na","næs",
    "god","wif","cild","hlaford","land","rice","word",
    "dæg","niht","englaland","seaxe","līht","sǣg"
]}


def _stem(word: str) -> str:
    """
    Light heuristic OE stemmer — reduces false negatives from inflection.
    Tries suffixes longest-first so 'cyningas' → 'cyning', not 'cyninga'.
    """
    w = word
    for suf in ("endum","enne","enne","igean","igende",
                "unge","inga","igra","igre","igum",
                "um","as","an","en","es","ra","re","ne","a","e"):
        if len(w) - len(suf) >= 3 and w.endswith(suf):
            return w[:-len(suf)]
    return w


class OEValidator:
    def __init__(self, lexicon: OELexicon):
        self.lex = lexicon

    def _classify(self, word: str) -> str:
        n = _norm(word)

        if n in _ALWAYS_OK:
            return "ok"

        # Direct match (normalised)
        if self.lex.contains_norm(word):
            return "ok"

        # Stemmed match
        stemmed = _stem(n)
        if stemmed in self.lex.norm:
            return "ok"

        # Plausible: ends with a known OE inflectional suffix
        # but stem not confirmed — treat as uncertain, not wrong
        if n.endswith(("um","as","an","en","a","e","es","ra","re","ne")):
            return "plausible"

        return "suspect"

    def validate(self, text: str) -> dict:
        tokens = WORD_RE.findall(text)
        ok, plausible, suspect = [], [], []
        results = []
        for t in tokens:
            status = self._classify(t)
            results.append((t, status))
            if status == "ok":         ok.append(t)
            elif status == "plausible": plausible.append(t)
            else:                       suspect.append(t)
        return {
            "results":  results,
            "ok":       ok,
            "plausible":plausible,
            "suspect":  suspect,
        }


def score(v: dict) -> float:
    total = len(v["ok"]) + len(v["plausible"]) + len(v["suspect"])
    if total == 0:
        return 0.0
    return (len(v["ok"]) + 0.6 * len(v["plausible"])) / total
