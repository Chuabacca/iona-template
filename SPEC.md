# SPEC.md — normative formats

This file is the single source of truth for every machine-checked format in
iona. `scripts/validate` enforces it; `templates/` shows one valid example per
page type. If this file and any other document disagree, this file wins.

## 1. Frontmatter grammar (YAML-subset, NOT YAML)

Frontmatter is delimited by `---` lines at the top of the file. Only these three
forms are legal — nothing else (no nesting, no multiline values, no block lists,
no comments):

```
key: scalar value
key: "quoted scalar"        # required when the value contains : [ ] , or "
key: [item, "quoted, item"] # one-line flow list; items are scalars or quoted scalars
```

- Keys: `[a-z_]+`. Values are strings after parsing (no type coercion).
- A value containing `:`, `[`, `]`, `,`, or `"` MUST be quoted. Inside quotes,
  `\"` escapes a quote.
- Unknown keys are WARNINGS (forward-compatible), never errors.
- Files are UTF-8, LF line endings preferred (CRLF tolerated, normalized on read).

## 2. Page types and fields

| Field | sermon | note | resource | Notes |
|---|---|---|---|---|
| `type` | req (`sermon`) | req (`note`) | req (`resource`) | |
| `title` | req | req | req | quoted if it contains `:` |
| `date` | req | req | req | ISO `YYYY-MM-DD` |
| `speaker` | req | — | opt | for resources: the author |
| `venue` | req | — | opt | |
| `medium` | req | opt | req | enum, see §2.1: `transcript-asr` `transcript-export` `authored` `own-notes` |
| `series` | opt | — | opt | |
| `passages` | opt* | opt | opt | human form, e.g. `["Romans 8:28-30"]` |
| `passage_keys` | opt* | opt | opt | canonical, e.g. `[ROM.8.28-30]` |
| `tags` | opt | opt | opt | lowercase kebab-case |
| `source` | req | opt | req | repo-relative path into `sources/` |
| `sections_absent` | opt | opt | opt | sections the agent judged absent |
| `versification_ok` | opt | opt | opt | verse keys exempted from range WARN |
| `validate_skip` | opt | opt | opt | named checks downgraded to warnings |

*If either of `passages`/`passage_keys` is present, both must be, and they must
agree (the validator derives one from the other and compares).

`sections_absent` values: `exegesis` `application` `history` `doctrine`
`illustration` `question`. A section listed absent must not appear in the body.

`validate_skip` values (check names): `anchor-resolution` `entry-grammar`
`passages-consistency` `link-resolution`.

### 2.1 `medium` — fidelity of the retained text

`medium` tracks exactly one axis: **how exactly do we have the words sitting in
`sources/`?** It deliberately does not track the setting (a church service, a
seminar, a conference) — `venue` and `series` already carry that, and encoding
it here produced disagreements between pages describing the same weekend. Nor
does it track the container (audio, book, article); the source path carries
that, and the distinction changes nothing about how the text may be used.

| value | the source text is | consequence |
|---|---|---|
| `transcript-asr` | machine transcription of speech | lossy; garbled regions expected and flagged as `question` entries; never reproduce as the speaker's exact words without checking |
| `transcript-export` | a human or platform transcript | more reliable, still not authoritative |
| `authored` | the words the source itself wrote — book, article, published post | quotable verbatim; an anchor mismatch is a real citation error, not drift |
| `own-notes` | the page author's own words | anchoring a paraphrase back to them is optional (§4) |

This is the axis the anchor rule already depended on implicitly. Anchors exist
so that a paraphrase of *someone else's* words stays auditable, which is why
they are required whenever a page has a `source` and its medium is not
`own-notes` — a note taken on a book needs anchoring exactly as a sermon does,
while the owner's own reflection does not. Keying the rule to `medium` rather
than to page `type` states that distinction once instead of twice.

If the setting or the container later earns its keep, add a separate optional
field; do not overload this one.

## 3. Passage-key grammar

```
KEY      := BOOK | BOOK.CH | BOOK.CH.V | BOOK.CH.V1-V2
BOOK     := three-character USFM code from scripts/books.json (e.g. GEN, ROM, 1CO)
CH, V    := positive integers, no zero-padding
V1-V2    := intra-chapter range, V1 < V2
```

- Cross-chapter spans are expressed as multiple keys.
- Single-chapter books (OBA, PHM, 2JN, 3JN, JUD) are always chapter 1: `JUD.1.3`.
- Versification: KJV (1769), vendored in `scripts/books.json`. A verse number
  beyond the table is a WARNING (override with `versification_ok`), never an error.
- Human form (`passages`): `<Book name or alias> CH[:V1[-V2]]`, e.g.
  `Romans 8:28-30`, `Mark 4`, `Jude 3`. Aliases per `books.json`.
  `scripts/passage-key` converts both directions.

## 4. Entry-line grammar (categorized sections of processed pages)

Every bullet in a categorized section (`## Exegesis`, `## Application`,
`## History`, `## Doctrine`, `## Illustrations`, `## Questions`) is ONE line:

```
- `[KEY]` … prose … › [¶N "verbatim quote from the source"]
```

Regex (enforced by validate, parsed by generate):

```
^- (?:`\[[A-Z0-9]{3}\.[0-9]+(?:\.[0-9]+(?:-[0-9]+)?)?\]` )*(.+?)(?: › \[¶([0-9]+) "([^"]+)"\])?$
```

- **Exegesis and Application entries require ≥1 leading key.** History,
  Doctrine, Illustrations, Questions entries may omit keys.
- **Anchors** (`› [¶N "quote"]`) are required on every entry of a page that has
  a `source` whose `medium` is not `own-notes` — agent paraphrase of someone
  else's words must be auditable (§2.1). Optional when the words are already
  your own. The quote must appear verbatim inside paragraph N of the page's
  `source` file. Positional-only anchors (`› [source ¶N]`) are forbidden.
- A paragraph is a blank-line-separated block; ¶1 is the first block after the
  frontmatter (sources have no frontmatter: ¶1 is the first block of the file).

## 5. Filename slugs

```
sources/<YYYY>/<YYYY-MM-DD>-<speaker-slug>-<passage-slug>.md
sermons/<YYYY-MM-DD>-<speaker-slug>-<passage-slug>.md
notes/<YYYY-MM-DD>-<topic-or-passage-slug>.md
resources/<YYYY-MM-DD>-<author-or-title-slug>.md
studies/<YYYY-MM-DD>-<topic-slug>.md
```

- Slugs: lowercase ASCII, hyphens, no articles. Speaker slug = full surname or
  well-known short form used CONSISTENTLY (`macarthur`, not sometimes
  `john-macarthur`); `scripts/ingest` enforces this by reusing the slug already
  on disk for a speaker of the same name.
- Passage slug, derived from the keys of the PRIMARY (first) book: several
  chapters → `<book>-<first>-<last>` (`acts-19-20`); one key with verses →
  `<book>-<ch>-<v1>[-<v2>]` (`romans-8-28-30`); otherwise `<book>-<ch>`
  (`mark-4`). `<book>` is the book-name slug, not the USFM code.
- The retained source is the transcript `.md`. Raw audio is a transient
  ingestion input, discarded once the transcript exists (never committed —
  `.gitignore` nets audio extensions). Only created artifacts are kept.

## 6. Scripture text store (`scripture/_text/<version>/<book>/<NN>.md`)

Durable verse text, one directory per translation. One line per verse:

```
MRK.4.1 | <verse text>
```

Key, space-pipe-space, verse text. Lines sorted by verse number. No frontmatter.

**Versions.** `<version>` is a lowercase slug (`bsb`, `lsb`, `esv`). Two roles,
named by single-line config files:

- **Display** — `scripture/_text/.default` (default `bsb`). Its text is embedded
  as the primary quote on generated pages, so there is always public-domain text
  to read. The owner switches display translation here without editing scripts.
- **Study** — `scripture/_text/.primary` (default: the display version). The one
  whose *absence* drives the "missing text" worklist: the generator reports which
  cited verses still lack this translation, and renders it as an additional quote
  where present. Set to the owner's preferred study translation (e.g. `lsb`) so
  the health signal tracks building that translation up, not the always-complete
  public-domain display text.

Other versions are stored and greppable but do not appear on generated pages.

**Provenance.** `bsb` is installed by `scripts/fetch-bsb` from bereanbible.com,
which dedicates the Berean Standard Bible to the public domain; it is therefore
the only version committed to the repo. Every other translation is copyrighted
and owner-supplied: `.gitignore` denies `scripture/_text/*` by default so added
versions stay local, and `scripts/validate` warns if a non-public-domain version
is not ignored. The agent never reconstructs verse text from memory in any
version — it asks the owner.

**Omitted verses.** Where a translation's base text omits a verse that the
versification still numbers (Matt 17:21, John 5:4, Acts 8:37, …), the line is
present with a bracketed omission marker rather than absent. This distinguishes
"this translation omits it" from "the owner has not supplied it yet".

The generator embeds available verses and lists missing keys for verses that
have entries.

## 7. Generated files

### 7.1 The scripture tree — one file per verse

Learnings are stored per verse, in a book/chapter directory tree, so that a
verse accumulating many notes over years is still one addressable file:

```
scripture/<book>/index.md              book index — every chapter, note counts
scripture/<book>/<CCC>/index.md        chapter index — every verse + its text
scripture/<book>/<CCC>/<VVV>.md        verse page — the notes on that verse
```

- `<book>` is the book-name slug (`acts`, `1-corinthians`). `<CCC>` and `<VVV>`
  are zero-padded to **three** digits, so lexical sort is numeric order (Psalms
  reaches chapter 150; Psalm 119 reaches verse 176).
- A **verse page exists only where there is something to store** — at least one
  note or one range reference. Chapter and book indexes exist for every chapter
  of every book present in the text store, so the whole Bible stays browsable
  without 31,102 near-empty files.
- The verse page groups notes under section headings (`## Exegesis`,
  `## Application`, …) in SPEC §4 order; within a section, entries sort by page
  date, then page path, then prose. A key is printed on an entry only when it is
  *broader* than the verse itself (a range or chapter key).
- Chapter-level keys (`ACT.19`) render in a `## Chapter` section on the chapter
  index, not on any verse page.

These files are **projections**, not storage of record: notes are authored in
`sermons/`, `notes/`, and `resources/`, anchored to `sources/`, and rebuilt onto
verse pages by `scripts/generate`. Writing into `scripture/` by hand loses the
edit at the next rebuild; `scripts/validate` errors on any file there lacking
the generated header.

### 7.2 Rendering rules

- **Multi-verse note storage.** A note keyed to a verse range (`ACT.19.8-10`)
  is stored in full only on the *first* verse of the range (`008.md`). The
  remaining verses (`009.md`, `010.md`) carry an `## Also referenced` pointer
  back to it, not a duplicate of the note.
- **Text shown per verse.** The display version (§6) is the primary quote; the
  study version, where present, is rendered as an additional quote. A verse that
  is cited (full note or reference) and lacks study-version text says so on its
  own page, is listed in the chapter index's "Missing <STUDY> text" section, and
  is counted in the INDEX health signal.
- Live only in `scripture/` (not `_text/`), `speakers/`, `series/`,
  `topics/_generated/`, and `INDEX.md`.
- First line: `<!-- GENERATED — do not edit. Rebuild: scripts/generate -->`
- Written atomically (temp file + rename); byte-identical output for identical
  input (all iteration sorted). Files no longer produced are swept, and
  directories left empty by the sweep are pruned.

## 8. Script CLI contract

Every script: exit 0 on success (warnings on stderr), exit 1 on errors,
`--strict` promotes warnings to errors, `--help` prints usage.
`scripts/validate` is read-only. The pre-commit hook (`scripts/hooks/pre-commit`,
activated by `scripts/setup` via `core.hooksPath`) runs validate, then generate,
and fails on any resulting diff in generated paths.

## 9. Ingestion pipeline (`scripts/ingest`)

Ingestion has exactly one step that needs judgment — reading a transcript and
writing categorized, anchored entries. Everything else is mechanical and lives
in `scripts/ingest`, so a run is reproducible rather than improvised. The
`/meditate` skill is the operating procedure that drives it.

| Command | Effect | Output |
|---|---|---|
| `status [<path>…]` | classify inbox items | JSON |
| `plan <path> <meta>` | derive paths, slugs, keys — **no writes** | JSON |
| `stage <path> <meta>` | copy transcript to `sources/`, scaffold the page | JSON |
| `check <path>` | is the judgment step finished? | JSON |
| `finish <path>` | validate → generate → reindex → report → clear inbox | text |
| `needs-info <path> --reason` | mark a blocked inbox item | JSON |

- **State is derived, never stored.** A transcript's identity is the SHA-256 of
  its *normalized* text (§1 read rules), so line endings never fork a source.
  `status` reports `new` (no matching source), `staged` (source exists, no page
  references it — an interrupted run, resume it), or `ingested` (a referencing
  page exists — a duplicate, stop).
- **`plan` is pure.** Same inputs → same paths, keys, and slugs, every time.
  Missing metadata is reported, never guessed.
- **`stage` is idempotent.** It refuses to write over a different transcript at
  the same path, and never overwrites an existing page — a resumed run keeps
  whatever entries were already written.
- **`check` gates `finish`.** A page is ready only when it has ≥1 entry, no
  `TODO(meditate)` placeholders, no section heading left empty, and every
  section of §4 either written or named in `sections_absent`.
- **`finish` clears the inbox last**, and only for an item whose content hashes
  equal to the retained transcript.

## 10. Corpus format version (`.iona-version`)

A single line holding the semver version of the corpus format this repository
was last migrated to:

```
0.1.0
```

`scripts/lib.py` declares the version the mechanics speak (`FORMAT_VERSION`).
`scripts/validate` compares the two and warns — never blocks — when they
disagree, so an upgrade surfaces at the next commit through the pre-commit hook
rather than as a wall of validation errors. `--strict` promotes it.

**Compatibility axis.** Below `1.0.0` the MINOR is the axis, per semver's rule
for initial development: `0.1.x` → `0.2.0` is a breaking format change and
`0.1.0` → `0.1.7` is not. From `1.0.0` onward the MAJOR is the axis in the
usual way.

A change is breaking if an existing, previously valid corpus would fail
`scripts/validate` against the new mechanics — a frontmatter field whose legal
values changed, a new required field, a rename in the generated tree. Adding a
capability that leaves existing corpora valid is not breaking.

**Upgrading.** A repository created from the template shares no git history
with it, so there is no merge path. To take a newer version, replace the
mechanics — `scripts/`, `SPEC.md`, `templates/`, `.claude/` — which
`CLAUDE.md` §2 already forbids editing, then follow `MIGRATIONS.md` for each
minor version crossed and update `.iona-version`. Never replace
`HERMENEUTICS.md` or anything under the content directories.
