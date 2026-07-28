# iona-template — an agent-primary scripture knowledge workspace

## The name

Iona is named after the island off the west coast of Scotland where, from the sixth century,
a community of monks copied the Scriptures by hand. It was instrumental in preserving
Scripture and biblical literacy after the fall of the Roman Empire.

Scripture is the authoritative, inerrant word of God, and it is the believer's task
to study it faithfully. This is the conviction behind this project. Iona allows the text
to anchor the learning process while leveraging AI as an assistant.

- **Every claim is keyed to a verse.** Notes do not float free of the passage
  they came from.
- **Every paraphrase carries a verbatim quote anchor** back to the words that
  produced it, and `scripts/validate` checks the quote is still there. Nothing
  the agent writes about a source is unverifiable against that source.
- **The agent never reconstructs verse text from memory** in any translation.
  It asks. A model's recollection of a verse is not the authoritative source.
- **Sources are recorded, not corrected.** If there is tension between scripture,
  someone's teaching, and your own convictions, the agent writes down what was actually
  said and flags the tension, rather than quietly harmonizing it away. The corpus is a record,
  not an echo chamber.

## What it is

A template for building a personal, git-versioned store of scripture knowledge.
Drop in sermon audio, transcripts, or study notes; a Claude-class agent
categorizes them, links every claim to a verse and to the verbatim words that
produced it, and compiles the result into one markdown file per Bible verse.

Everything here is plain markdown and `python3` with no third-party
dependencies. The only optional extras are local ML models for transcription
and semantic search; nothing calls an API, and no data leaves your machine.

## The idea

Notes are authored where they can be checked, and *projected* where they can be
found.

- You author in `sermons/`, `notes/`, `resources/` — one page per source, every
  entry carrying a passage key and a verbatim quote anchor back into `sources/`.
- `scripts/generate` projects those entries onto **one file per verse**:
  `scripture/<book>/<chapter>/<verse>.md`, with the verse text, every note ever
  made on it grouped by category, and cross-references.

So a verse you have studied for ten years across thirty sermons is still one
file, sorted into exegesis / application / history / doctrine / illustrations /
questions. And because the verse pages are generated, they can never drift from
what your sources actually said.

The quote anchors are what make this trustworthy rather than merely tidy. Every
paraphrase names the paragraph it came from and quotes it verbatim, and
`scripts/validate` checks that the quote is still there. Correct a transcript
and the validator tells you immediately which entries you just invalidated.

## Quick start

```
scripts/setup              # activate the pre-commit hook
scripts/setup --ml         # optional: local transcription model + semantic search
scripts/fetch-bsb          # install the public-domain Berean Standard Bible
```

Then, before ingesting anything:

1. **Fill in `HERMENEUTICS.md`.** It ships as a skeleton on purpose — it is the
   charter the agent reads before writing every entry, and it has to be yours.
   `examples/HERMENEUTICS.reformed-evangelical.md` shows one filled-in charter
   as an example of the form, not as a default.
2. Drop a transcript or audio file into `inbox/`.
3. Run **`/meditate`** in Claude Code.

The agent transcribes if needed, derives paths and passage keys, writes the
categorized entries, validates, regenerates, and reports — then shows you the
diff and waits for your go-ahead before committing.

## Layout

```
inbox/                       drop zone (audio or transcripts)
sources/<year>/              verbatim transcripts — the retained source of record
sermons/ notes/ resources/   processed pages: categorized, verse-keyed, anchored
studies/                     dated syntheses, superseded rather than rewritten
topics/                      hand-written topic pages
scripture/_text/<version>/   Bible text store (SPEC §6)

scripture/<book>/index.md            GENERATED  book index
scripture/<book>/<CCC>/index.md      GENERATED  chapter index (text + note markers)
scripture/<book>/<CCC>/<VVV>.md      GENERATED  the notes on that one verse
speakers/ series/ topics/_generated/ INDEX.md   GENERATED
```

Everything marked GENERATED is rebuilt from the processed pages — never
hand-edit it. `scripts/validate` errors if you do.

## Scripts

| | |
|---|---|
| `scripts/setup` | git hooks; `--ml` installs transcription + search deps |
| `scripts/fetch-bsb` | install the public-domain BSB into the text store |
| `scripts/transcribe` | local audio → paragraph transcript (mlx-whisper) |
| `scripts/ingest` | the deterministic ingestion pipeline (SPEC §9) |
| `scripts/validate` | read-only conformance checks; run by the pre-commit hook |
| `scripts/generate` | rebuild every generated page, deterministically |
| `scripts/search` | fully local semantic index (no API keys, no server) |
| `scripts/passage-key` | convert and expand passage references |

Every script takes `--help`, exits 0 on success and 1 on errors, and treats
`--strict` as "promote warnings to errors."

## Where the design is written down

- **`SPEC.md`** — normative. Frontmatter grammar, passage keys, entry lines and
  anchors, filename slugs, the text store, the generated tree, the ingestion
  pipeline. If any other document disagrees with SPEC, SPEC wins.
- **`CLAUDE.md`** — how the agent operates: safety rules, the ingestion
  workflow, the retrieval workflow.
- **`HERMENEUTICS.md`** — yours to write.

## Customizing

Most people should change only `HERMENEUTICS.md` and then start ingesting. Past
that:

- **Display translation** — `scripture/_text/.default` (a version slug, default
  `bsb`). The text embedded on generated pages.
- **Study translation** — create `scripture/_text/.primary` with a version slug
  to make the generator track which cited verses still lack that translation.
  Unset by default, which keeps the "missing text" worklist empty.
- **Categories** — `lib.SECTIONS` and `lib.SECTION_HEADINGS` in
  `scripts/lib.py`, mirrored in SPEC §4. Changing these changes every page, so
  decide early.
- **Page types** — `lib.REQUIRED_FIELDS`.

## License

The mechanics — scripts, spec, templates, documentation — are **MIT**
([`LICENSE`](LICENSE)). Two carve-outs matter, both spelled out in
[`NOTICE`](NOTICE):

- **`scripts/tsk/cross_references.json` is CC BY 4.0**, not MIT. It derives from
  the [openbible.info](https://www.openbible.info/labs/cross-references/)
  cross-reference dataset. Redistribute it and you must keep the attribution —
  see [`scripts/tsk/LICENSE`](scripts/tsk/LICENSE).
- **The license covers the tool, not your corpus.** Sermon transcripts,
  recordings, and book excerpts you ingest remain their authors' copyrighted
  works. MIT on this template grants you nothing with respect to them.

## Privacy & copyright

- Sermon transcripts are third-party content stored for **personal use**. Keep
  your corpus repo **private**. This template is public; a corpus built from it
  generally should not be.
- Bible text lives in `scripture/_text/<version>/`. The default (`bsb`) is the
  Berean Standard Bible, dedicated to the public domain by its publisher, and is
  safe to commit. Any other version is copyrighted, gitignored by default, and
  owner-supplied; `scripts/validate` warns if a non-public-domain version
  escapes that rule.
- Audio is treated as a transient ingestion input and discarded once the
  transcript exists. `.gitignore` blocks audio extensions outright so a
  recording can never be committed, even mid-run.
