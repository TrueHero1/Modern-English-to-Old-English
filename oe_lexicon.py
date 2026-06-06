"""
Loads and normalises the Old English word list.
"""

import re
from pathlib import Path

# Strip macrons and unify thorn/eth so lookups are accent-insensitive
_NORM_TABLE = str.maketrans({
    "ā":"a","ē":"e","ī":"i","ō":"o","ū":"u","ǣ":"æ","ȳ":"y","ǽ":"æ",
    "Ā":"a","Ē":"e","Ī":"i","Ō":"o","Ū":"u","Ǣ":"æ","Ȳ":"y","Ǽ":"æ",
    "ð":"þ","Ð":"þ",
})

def _norm(w: str) -> str:
    return w.lower().translate(_NORM_TABLE)

# Strip (-)..(-) wrappers, then leading/trailing hyphens
_PAREN_RE  = re.compile(r"\([^)]*\)")
_TOKEN_RE  = re.compile(r"[^\s]+")

def _parse_line(line: str):
    """Yield individual word tokens from one line of the file."""
    for raw in _TOKEN_RE.findall(line):
        clean = _PAREN_RE.sub("", raw).strip("-").strip()
        if not clean:
            continue
        yield clean
        # Also add each component of a hyphenated compound separately
        if "-" in clean:
            for part in clean.split("-"):
                part = part.strip()
                if part:
                    yield part


class OELexicon:
    def __init__(self, path: str = "data/oe_lexicon.txt"):
        self.raw:  set[str] = set()   # lowercased originals  (with OE chars)
        self.norm: set[str] = set()   # macron-stripped forms (for fuzzy match)
        self._load(path)

    def _load(self, path: str):
        p = Path(path)
        if not p.exists():
            print(f"[lexicon] ⚠  Not found: {path}")
            return

        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            for word in _parse_line(line):
                self.raw.add(word.lower())
                self.norm.add(_norm(word))

        print(f"[lexicon] Loaded {len(self.raw):,} forms / "
              f"{len(self.norm):,} normalised — from {p.name}")

    def contains(self, word: str) -> bool:
        """Exact lowercase match (preserves OE chars)."""
        return word.lower() in self.raw

    def contains_norm(self, word: str) -> bool:
        """Macron-stripped match — used by the validator."""
        return _norm(word) in self.norm