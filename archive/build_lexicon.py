# build_lexicon.py

import re

SOURCE = "bosworth_raw.txt"
TARGET = "oe_lexicon.txt"

words = set()

with open(SOURCE, encoding="utf-8") as f:
    for line in f:
        line = line.strip().lower()

        if not line:
            continue

        # remove grammatical descriptions
        line = re.sub(r",.*$", "", line)

        # remove trailing punctuation
        line = re.sub(r"[.;:]$", "", line)

        # remove surrounding whitespace again
        line = line.strip()

        # skip obvious garbage
        if len(line) < 2:
            continue

        words.add(line)

with open(TARGET, "w", encoding="utf-8") as f:
    for word in sorted(words):
        f.write(word + "\n")

print(f"Cleaned lexicon contains {len(words):,} entries")