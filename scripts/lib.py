"""iona shared library — frontmatter subset, passage keys, entries, paragraphs.

Normative grammar: SPEC.md. python3 stdlib only.
"""

import json
import os
import re
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_PATH = os.path.join(ROOT, "scripts", "books.json")

CONTENT_DIRS = ("sermons", "notes", "resources")
GENERATED_DIRS = ("scripture", "speakers", "series", os.path.join("topics", "_generated"))
GENERATED_HEADER = "<!-- GENERATED — do not edit. Rebuild: scripts/generate -->"

# `medium` tracks ONE axis: how exactly we have the words in sources/ (SPEC §2).
# Not the setting (venue + series already carry that) and not the container
# (the source path does). This is the axis that governs whether a quote may be
# reproduced as the source's own words, and it is the same distinction that
# drives the anchor rule in SPEC §4.
MEDIUM_ENUM = ("transcript-asr", "transcript-export", "authored", "own-notes")
# The one medium whose words are already the page author's, so anchoring a
# paraphrase back to them is optional rather than required.
UNANCHORED_MEDIUM = "own-notes"
SECTIONS = ("exegesis", "application", "history", "doctrine", "illustration", "question")
# Section heading in body -> canonical section name
SECTION_HEADINGS = {
    "exegesis": "exegesis",
    "application": "application",
    "history": "history",
    "doctrine": "doctrine",
    "illustrations": "illustration",
    "questions": "question",
}
# Canonical section name -> heading used on generated verse pages
SECTION_TITLES = {
    "exegesis": "Exegesis",
    "application": "Application",
    "history": "History",
    "doctrine": "Doctrine",
    "illustration": "Illustrations",
    "question": "Questions",
}
VALIDATE_SKIP_CHECKS = (
    "anchor-resolution", "entry-grammar", "passages-consistency", "link-resolution",
)

# Per-type field requirements (SPEC §2)
REQUIRED_FIELDS = {
    "sermon": ("type", "title", "date", "speaker", "venue", "medium", "source"),
    "note": ("type", "title", "date"),
    "resource": ("type", "title", "date", "medium", "source"),
}
KNOWN_FIELDS = (
    "type", "title", "date", "speaker", "venue", "medium", "series",
    "passages", "passage_keys", "tags", "source", "sections_absent",
    "versification_ok", "validate_skip",
)

KEY_RE = re.compile(r"^([A-Z0-9]{3})(?:\.([0-9]+)(?:\.([0-9]+)(?:-([0-9]+))?)?)?$")
ENTRY_RE = re.compile(
    r"^- (?P<keys>(?:`\[[A-Z0-9]{3}\.[0-9]+(?:\.[0-9]+(?:-[0-9]+)?)?\]` )*)"
    r"(?P<prose>.+?)"
    r"(?: › \[¶(?P<para>[0-9]+) \"(?P<quote>[^\"]+)\"\])?$"
)
ENTRY_KEY_RE = re.compile(r"`\[([A-Z0-9.\-]+)\]`")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
VERSE_LINE_RE = re.compile(r"^([A-Z0-9]{3}\.[0-9]+\.[0-9]+) \| (.+)$")


class SpecError(ValueError):
    pass


# ---------------------------------------------------------------- books

_books_cache = None


def load_books():
    """Return (by_code, alias_map). alias_map keys are lowercase."""
    global _books_cache
    if _books_cache is None:
        with open(BOOKS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        by_code = {b["code"]: b for b in data["books"]}
        alias = {}
        for b in data["books"]:
            alias[b["name"].lower()] = b["code"]
            alias[b["code"].lower()] = b["code"]
            for a in b["aliases"]:
                alias[a.lower()] = b["code"]
        _books_cache = (by_code, alias)
    return _books_cache


def single_chapter_books():
    by_code, _ = load_books()
    return {c for c, b in by_code.items() if b["chapters"] == 1}


# ------------------------------------------------- scripture page addressing
# SPEC §7: learnings are stored one file per verse, under a book/chapter tree.
# Chapter and verse components are zero-padded to a fixed width so that plain
# lexical sort (ls, git, glob) is also numeric order — Psalms reaches chapter
# 150 and Psalm 119 reaches verse 176, so two digits is not enough.
CH_PAD = 3
V_PAD = 3


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "unknown"


def book_slug(code):
    """USFM code -> directory slug, e.g. ACT -> 'acts', 1CO -> '1-corinthians'."""
    by_code, _ = load_books()
    return slugify(by_code[code]["name"])


def book_dir_rel(code):
    return os.path.join("scripture", book_slug(code))


def chapter_dir_rel(code, ch):
    return os.path.join(book_dir_rel(code), "%0*d" % (CH_PAD, ch))


def book_index_rel(code):
    return os.path.join(book_dir_rel(code), "index.md")


def chapter_index_rel(code, ch):
    return os.path.join(chapter_dir_rel(code, ch), "index.md")


def verse_page_rel(code, ch, v):
    return os.path.join(chapter_dir_rel(code, ch), "%0*d.md" % (V_PAD, v))


# ------------------------------------------------------- text store versions

TEXT_ROOT = os.path.join(ROOT, "scripture", "_text")
# Versions that may be committed. The BSB is dedicated to the public domain by
# its publisher; every other translation is copyrighted, so it stays local
# (see .gitignore) and is owner-supplied only.
PUBLIC_DOMAIN_VERSIONS = ("bsb",)
FALLBACK_TEXT_VERSION = "bsb"
DEFAULT_VERSION_FILE = os.path.join(TEXT_ROOT, ".default")


def text_versions():
    """Version slugs present in the text store, sorted."""
    if not os.path.isdir(TEXT_ROOT):
        return []
    return sorted(d for d in os.listdir(TEXT_ROOT)
                  if not d.startswith(".")
                  and os.path.isdir(os.path.join(TEXT_ROOT, d)))


def default_text_version():
    """Display version — the verse text embedded on generated pages.

    Read from scripture/_text/.default so the owner can switch translations
    without editing scripts. Falls back to bsb, then to any version present.
    """
    if os.path.exists(DEFAULT_VERSION_FILE):
        with open(DEFAULT_VERSION_FILE, encoding="utf-8") as f:
            name = f.read().strip()
        if name:
            return name
    present = text_versions()
    if FALLBACK_TEXT_VERSION in present or not present:
        return FALLBACK_TEXT_VERSION
    return present[0]


PRIMARY_VERSION_FILE = os.path.join(TEXT_ROOT, ".primary")


def primary_text_version():
    """Study version — the one whose ABSENCE is the 'missing text' worklist.

    Distinct from the display default: pages render the public-domain default
    (bsb) so there is always something to read, but the health signal tracks
    the owner's preferred study translation (e.g. lsb) and reports which cited
    verses still lack it. Read from scripture/_text/.primary; falls back to the
    display default when unset (then the worklist is trivially empty for bsb).
    """
    if os.path.exists(PRIMARY_VERSION_FILE):
        with open(PRIMARY_VERSION_FILE, encoding="utf-8") as f:
            name = f.read().strip()
        if name:
            return name
    return default_text_version()


# ---------------------------------------------------------------- text IO

def read_text(path):
    """Read UTF-8 text, normalizing CRLF. Raises SpecError on bad encoding."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise SpecError("not valid UTF-8: %s" % e) from e
    return text.replace("\r\n", "\n").replace("\r", "\n")


def atomic_write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def paragraphs(text):
    """Blank-line-separated blocks. ¶1 is index 0."""
    return [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


# ---------------------------------------------------------------- frontmatter

def _parse_value(val, line_no, errors):
    val = val.strip()
    if val.startswith("["):
        if not val.endswith("]"):
            errors.append((line_no, "unterminated flow list"))
            return []
        return _parse_list_items(val[1:-1], line_no, errors)
    if val.startswith('"'):
        s, rest = _parse_quoted(val, line_no, errors)
        if rest.strip():
            errors.append((line_no, "trailing content after quoted scalar"))
        return s
    for ch in ':[]",':
        if ch in val:
            errors.append((line_no, "value containing %r must be quoted" % ch))
            break
    return val


def _parse_quoted(s, line_no, errors):
    """s starts with a quote. Returns (value, remainder-after-closing-quote)."""
    out = []
    i = 1
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == '"':
            out.append('"')
            i += 2
            continue
        if c == '"':
            return "".join(out), s[i + 1:]
        out.append(c)
        i += 1
    errors.append((line_no, "unterminated quoted scalar"))
    return "".join(out), ""


def _parse_list_items(inner, line_no, errors):
    items = []
    i = 0
    n = len(inner)
    while i < n:
        while i < n and inner[i] in " \t":
            i += 1
        if i >= n:
            break
        if inner[i] == '"':
            val, rest = _parse_quoted(inner[i:], line_no, errors)
            items.append(val)
            i = n - len(rest)
            while i < n and inner[i] in " \t":
                i += 1
            if i < n:
                if inner[i] != ",":
                    errors.append((line_no, "expected , after quoted list item"))
                    break
                i += 1
        else:
            j = inner.find(",", i)
            if j == -1:
                item = inner[i:].strip()
                i = n
            else:
                item = inner[i:j].strip()
                i = j + 1
            if item:
                for ch in ':[]"':
                    if ch in item:
                        errors.append(
                            (line_no, "list item containing %r must be quoted" % ch))
                        break
                items.append(item)
    return items


def parse_frontmatter(text):
    """Return (fields, body, errors, warnings).

    fields: dict key -> str | list[str]; errors/warnings: list[(line_no, msg)].
    Line numbers are 1-based within the file.
    """
    errors, warnings = [], []
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        errors.append((1, "missing frontmatter opening ---"))
        return {}, text, errors, warnings
    fields = {}
    close = None
    for idx in range(1, len(lines)):
        line = lines[idx]
        if line.strip() == "---":
            close = idx
            break
        if not line.strip():
            continue
        m = re.match(r"^([a-z_]+):(?:\s+(.*))?$", line)
        if not m:
            errors.append((idx + 1, "not a legal frontmatter line (SPEC §1): %r" % line))
            continue
        key, val = m.group(1), m.group(2) or ""
        if not val.strip():
            errors.append((idx + 1, "empty value for %r" % key))
            continue
        if key in fields:
            errors.append((idx + 1, "duplicate key %r" % key))
            continue
        fields[key] = _parse_value(val, idx + 1, errors)
    if close is None:
        errors.append((len(lines), "missing closing ---"))
        body = ""
    else:
        body = "\n".join(lines[close + 1:])
    for key in fields:
        if key not in KNOWN_FIELDS:
            warnings.append((0, "unknown frontmatter field %r" % key))
    return fields, body, errors, warnings


# ---------------------------------------------------------------- passage keys

def parse_key(key):
    """Parse a passage key. Returns dict(book, ch, v1, v2) — ch/v may be None.

    Raises SpecError for malformed keys or unknown book codes.
    """
    by_code, _ = load_books()
    m = KEY_RE.match(key)
    if not m:
        raise SpecError("malformed passage key %r (SPEC §3)" % key)
    book, ch, v1, v2 = m.group(1), m.group(2), m.group(3), m.group(4)
    if book not in by_code:
        near = ", ".join(sorted(c for c in by_code if c[0] == book[0]))
        raise SpecError("unknown book code %r (starting %s: %s)" % (book, book[0], near))
    ch = int(ch) if ch else None
    v1 = int(v1) if v1 else None
    v2 = int(v2) if v2 else None
    if ch is not None and not (1 <= ch <= by_code[book]["chapters"]):
        raise SpecError("%s has %d chapters; got chapter %d in %r"
                        % (book, by_code[book]["chapters"], ch, key))
    if v1 is not None and v1 < 1:
        raise SpecError("verse must be >= 1 in %r" % key)
    if v2 is not None and v2 <= v1:
        raise SpecError("range end must exceed start in %r" % key)
    return {"book": book, "ch": ch, "v1": v1, "v2": v2}


def verse_range_warnings(key):
    """Return list of warning strings for verses beyond the versification table."""
    by_code, _ = load_books()
    p = parse_key(key)
    if p["ch"] is None or p["v1"] is None:
        return []
    maxv = by_code[p["book"]]["verse_counts"][p["ch"] - 1]
    last = p["v2"] or p["v1"]
    if last > maxv:
        return ["%s: verse %d beyond KJV versification (%s %d has %d verses) — "
                "override with versification_ok" % (key, last, p["book"], p["ch"], maxv)]
    return []


def expand_key(key):
    """Expand a key to per-verse keys BOOK.CH.V (capped at versification table)."""
    by_code, _ = load_books()
    p = parse_key(key)
    book = by_code[p["book"]]
    out = []
    if p["ch"] is None:
        for ch in range(1, book["chapters"] + 1):
            for v in range(1, book["verse_counts"][ch - 1] + 1):
                out.append("%s.%d.%d" % (p["book"], ch, v))
        return out
    maxv = book["verse_counts"][p["ch"] - 1]
    if p["v1"] is None:
        vs = range(1, maxv + 1)
    else:
        vs = range(p["v1"], (p["v2"] or p["v1"]) + 1)
    for v in vs:
        out.append("%s.%d.%d" % (p["book"], p["ch"], v))
    return out


HUMAN_RE = re.compile(r"^(.+?)\s+([0-9]+)(?::([0-9]+)(?:-([0-9]+))?)?$")


def parse_human_ref(ref):
    """'Romans 8:28-30' -> 'ROM.8.28-30'. 'Jude 3' -> 'JUD.1.3'."""
    by_code, alias = load_books()
    ref = ref.strip()
    m = HUMAN_RE.match(ref)
    book_part, ch, v1, v2 = (m.groups() if m else (ref, None, None, None))
    code = alias.get(book_part.strip().lower().rstrip("."))
    if code is None:
        raise SpecError("unknown book name %r in %r" % (book_part.strip(), ref))
    if ch is None:
        return code
    ch = int(ch)
    if code in single_chapter_books() and v1 is None:
        # 'Jude 3' means verse 3 of the single chapter
        key = "%s.1.%d" % (code, ch)
    else:
        key = "%s.%d" % (code, ch)
        if v1 is not None:
            key += ".%d" % int(v1)
            if v2 is not None:
                key += "-%d" % int(v2)
    parse_key(key)  # validate
    return key


def human_ref(key):
    """'ROM.8.28-30' -> 'Romans 8:28-30'."""
    by_code, _ = load_books()
    p = parse_key(key)
    name = by_code[p["book"]]["name"]
    if p["ch"] is None:
        return name
    if p["book"] in single_chapter_books() and p["v1"] is not None:
        s = "%s %d" % (name, p["v1"])
        if p["v2"]:
            s += "-%d" % p["v2"]
        return s
    s = "%s %d" % (name, p["ch"])
    if p["v1"] is not None:
        s += ":%d" % p["v1"]
        if p["v2"]:
            s += "-%d" % p["v2"]
    return s


# ---------------------------------------------------------------- entries

def parse_entry(line):
    """Parse an entry line. Returns dict(keys, prose, para, quote) or None."""
    m = ENTRY_RE.match(line)
    if not m:
        return None
    keys = ENTRY_KEY_RE.findall(m.group("keys") or "")
    para = m.group("para")
    return {
        "keys": keys,
        "prose": m.group("prose").strip(),
        "para": int(para) if para else None,
        "quote": m.group("quote"),
    }


def iter_sections(body):
    """Yield (canonical_section, heading_line_no, [(line_no, line), ...])."""
    current, bucket, start = None, [], None
    for i, line in enumerate(body.split("\n"), start=1):
        h = re.match(r"^## (.+)$", line)
        if h:
            if current:
                yield current, start, bucket
            name = h.group(1).strip().lower()
            current = SECTION_HEADINGS.get(name)
            start = i
            bucket = []
        elif current is not None:
            bucket.append((i, line))
    if current:
        yield current, start, bucket


# ---------------------------------------------------------------- pages

def iter_page_paths(root=None, include_templates=False):
    root = root or ROOT
    dirs = list(CONTENT_DIRS) + (["templates"] if include_templates else [])
    for d in dirs:
        full = os.path.join(root, d)
        if not os.path.isdir(full):
            continue
        for name in sorted(os.listdir(full)):
            if name.endswith(".md") and not name.startswith("example-"):
                yield os.path.join(full, name)


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]
