"""
Modern English → Old English (West Saxon) → Anglo-Saxon Futhorc runes.

Requires:
  pip install requests
  ollama pull llama3.1:8b    (Optimal for 6GB VRAM)
  data/oe_lexicon.txt        (Old English word list)
"""

import re
import requests

from oe_lexicon  import OELexicon
from validator   import OEValidator, score

# ── Config ────────────────────────────────────────────────────────────────────

MODEL      = "qwen3:8b"   # Much faster for your hardware
OLLAMA_URL = "http://localhost:11434/api/generate"

# ── Futhorc mapping ───────────────────────────────────────────────────────────

DIGRAPHS = [
    ("ng", "ᛝ"),
    ("ēa", "ᛠ"), ("ea", "ᛠ"),
    ("ēo", "ᛇ"), ("eo", "ᛇ"),
    ("io", "ᛡ"),
    ("th", "ᚦ"),   
    ("æ",  "ᚫ"), ("ǣ", "ᚫ"), ("ǽ", "ᚫ"),
    ("œ",  "ᛟ"),
]

SINGLES = {
    "a":"ᚪ","b":"ᛒ","c":"ᚳ","d":"ᛞ","e":"ᛖ",
    "f":"ᚠ","g":"ᚷ","h":"ᚻ","i":"ᛁ","j":"ᛄ",
    "k":"ᚳ","l":"ᛚ","m":"ᛗ","n":"ᚾ","o":"ᚩ",
    "p":"ᛈ","q":"ᚳ","r":"ᚱ","s":"ᛋ","t":"ᛏ",
    "u":"ᚢ","v":"ᚠ","w":"ᚹ","x":"ᛉ","y":"ᚣ","z":"ᛉ",
    "þ":"ᚦ","ð":"ᚦ",
    "ā":"ᚪ","ē":"ᛖ","ī":"ᛁ","ō":"ᚩ","ū":"ᚢ","ȳ":"ᚣ",
}

WORD_SEP = "᛫"
SENT_SEP = "᛬"

def to_futhorc(text: str) -> str:
    out = []
    i   = 0
    t   = text.lower()
    while i < len(t):
        ch = t[i]
        if ch == " ":
            if out and out[-1] != WORD_SEP:
                out.append(WORD_SEP)
            i += 1
            continue
        if ch in ".!?":
            if out and out[-1] == WORD_SEP:
                out[-1] = SENT_SEP
            else:
                out.append(SENT_SEP)
            i += 1
            continue
        if not ch.isalpha() and ch not in "þðæœǣǽāēīōūȳ":
            i += 1
            continue
        matched = False
        for digraph, rune in DIGRAPHS:
            dlen = len(digraph)
            if t[i:i+dlen] == digraph:
                out.append(rune)
                i += dlen
                matched = True
                break
        if not matched:
            rune = SINGLES.get(ch)
            if rune:
                out.append(rune)
            i += 1
    return "".join(out)

# ── Loanword handling ─────────────────────────────────────────────────────────

LOAN_RE = re.compile(r"\[LOAN:\s*([^\]]+)\]", re.IGNORECASE)

def render_runes(old_english: str) -> tuple[str, str]:
    clean_parts = []
    runic_parts = []
    cursor      = 0

    for m in LOAN_RE.finditer(old_english):
        before = old_english[cursor:m.start()]
        loan   = m.group(1).strip()
        clean_parts.append(before)
        runic_parts.append(to_futhorc(before))
        clean_parts.append(loan)
        runic_parts.append(f"[{to_futhorc(loan)}]")
        cursor = m.end()

    tail = old_english[cursor:]
    clean_parts.append(tail)
    runic_parts.append(to_futhorc(tail))

    clean = "".join(clean_parts).strip()
    runes = "".join(runic_parts).strip(WORD_SEP).strip(SENT_SEP)
    return clean, runes

# ── Translation prompt ────────────────────────────────────────────────────────

PROMPT = """\
Translate the following Modern English into Late West Saxon Old English (c. 950 CE).

RULES:
1. Use only historically attested Old English vocabulary and grammar.
2. Apply correct noun cases, verb conjugations, and adjective agreement.
3. Use þ (voiceless) and ð (voiced) for the 'th' sound. Mark long vowels: ā ē ī ō ū ǣ ȳ.
4. CRITICAL: If a word has no exact Old English equivalent (like modern countries, technology, or modern concepts), you MUST write it as [LOAN: word]. Do not guess.
5. Output ONLY the Old English. No notes, no explanation, no alternatives.

EXAMPLES:
Modern: The king rides to the hall.
Old English: Se cyning rīdeþ tō þǣm healle.

Modern: We are learning about computers and the internet.
Old English: Wē leorniaþ ymbe [LOAN: computers] and þone [LOAN: internet].

Modern: {text}
Old English:"""

def translate(text: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model":  MODEL,
            "prompt": PROMPT.format(text=text),
            "stream": False,
            "options": {
                "temperature": 0.15,
                "top_p":       0.9,
                "num_predict": -1,
            },
        },
        timeout=300, # Increased to 5 minutes to prevent timeouts
    )
    resp.raise_for_status()
    raw = resp.json()["response"].strip()

    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^Old English:\s*", "", line, flags=re.IGNORECASE).strip()
        if line:
            return line

    return raw

# ── Display ───────────────────────────────────────────────────────────────────

W = 64

def rule():  print("─" * W)
def head(s): print(f"  {s}")

# ── Main Loop ─────────────────────────────────────────────────────────────────

def main():
    print("\nLoading dictionary...")
    lexicon   = OELexicon()
    validator = OEValidator(lexicon)

    print()
    print("╔" + "═"*(W-2) + "╗")
    print(f"║{'Anglo-Saxon Futhorc Converter':^{W-2}}║")
    print(f"║{'Model: ' + MODEL:^{W-2}}║")
    print("╚" + "═"*(W-2) + "╝")
    print("\nType 'exit' or 'quit' to stop.")

    while True:
        print()
        try:
            modern = input("Modern English → ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not modern:
            continue
        if modern.lower() in ["exit", "quit"]:
            print("Farewell!")
            break

        print("\nTranslating...\n")

        try:
            old_english_raw = translate(modern)
        except requests.exceptions.ConnectionError:
            print("✗  Ollama not running. Start it and try again."); continue
        except requests.exceptions.Timeout:
            print("✗  Timed out. The model may be busy — try a shorter sentence."); continue
        except Exception as e:
            print(f"✗  Error: {e}"); continue

        old_english, runes = render_runes(old_english_raw)
        oe_for_val = LOAN_RE.sub("", old_english_raw)
        v = validator.validate(oe_for_val)
        s = score(v)

        rule()
        head(f"Modern English"); head(f"  {modern}"); print()
        head(f"Old English  (West Saxon, c. 950 CE)"); head(f"  {old_english}"); print()
        head(f"Futhorc"); head(f"  {runes}"); print()
        rule()

        head("Validation")
        print()

        bar_width = 30
        total_words = max(len(v["ok"]) + len(v["plausible"]) + len(v["suspect"]), 1)
        ok_w  = round(bar_width * len(v["ok"]) / total_words)
        pl_w  = round(bar_width * len(v["plausible"]) / total_words)
        su_w  = bar_width - ok_w - pl_w
        bar   = "█"*ok_w + "▒"*pl_w + "░"*su_w

        print(f"  [{bar}]  {s:.0%}")
        print(f"  ✓ attested:  {len(v['ok'])}")
        print(f"  ~ plausible: {len(v['plausible'])}")
        print(f"  ✗ suspect:   {len(v['suspect'])}")

        if v["suspect"]:
            print(f"\n  Flagged: {', '.join(v['suspect'][:12])}")

        loans = LOAN_RE.findall(old_english_raw)
        if loans:
            print(f"\n  ⊕ Loanwords: {', '.join(loans)}")

        rule()

if __name__ == "__main__":
    main()