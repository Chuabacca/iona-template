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
You drop in a sermon recording, a transcript, or your own study notes. An AI
agent reads it, breaks it into individual claims, keys each claim to the verse
it is about, and anchors it to the exact words that produced it. Everything is
plain markdown in a git repository you own.

The organizing idea: **notes are authored where they can be checked, and
projected where they can be found.**

- You author in `sermons/`, `notes/` and `resources/` — one page per source.
- `scripts/generate` projects every entry onto **one markdown file per verse**:
  `scripture/<book>/<chapter>/<verse>.md`.

So a verse you have studied for ten years across thirty sermons is still *one
file*, with everything ever said about it grouped by category. And because verse
pages are generated rather than written, they cannot drift from what your
sources actually said.

### What that looks like

A paragraph in a transcript you dropped in `inbox/`:

> **¶2** The verb there is sunergeo. It does not say that all things are good.
> It says that God is working them together, which is a claim about his agency
> and not about the quality of the circumstances.

The agent writes this line onto the sermon's page in `sermons/`:

```
- `[ROM.8.28]` The verb sunergeo claims that God works circumstances together;
  the verse does not say the circumstances are themselves good › [¶2 "It does
  not say that all things are good."]
```

Three things are happening in that one line: `[ROM.8.28]` is the **verse key**,
the prose is the agent's **paraphrase**, and `› [¶2 "…"]` is the **anchor** —
paragraph 2 of the source, quoted verbatim.

Then `scripts/generate` produces `scripture/romans/008/028.md`:

```markdown
# Romans 8:28

`ROM.8.28` · [Romans 8](index.md)

> And we know that God works all things together for the good of those who love
> Him, who are called according to His purpose. (BSB)

## Exegesis

- The verb sunergeo claims that God works circumstances together; the verse does
  not say the circumstances are themselves good — [All Things Together](…) · 2026-08-02

## Cross-references

1PE.5.10, JAS.1.12, GEN.50.20, ROM.5.3-5, 1CO.2.9, ROM.8.35-39, …
```

The anchor is what makes this trustworthy rather than merely tidy. Because every
paraphrase names the paragraph it came from and quotes it, `scripts/validate`
can check the quote is still there. Fix a typo in a transcript and the validator
tells you immediately which entries you just invalidated:

```
ERROR: sermons/2026-08-02-example-romans-8-28.md:19: anchor quote not found in ¶2
```

Nothing calls an API. No data leaves your machine.

## Requirements

| | |
|---|---|
| **Claude Code** | `/meditate` is a Claude Code skill (`.claude/skills/`) |
| **git** | the corpus is a git repository; a pre-commit hook runs the validator |
| **python3** | core scripts are stdlib only — no packages to install |
| *Apple Silicon Mac* | **only** for the optional local transcription model |

**Built for Claude Code**, but not welded to it. The scripts are ordinary
command-line programs and `CLAUDE.md` is plain markdown, so another agent can
drive the same pipeline — point it at `CLAUDE.md` and `SPEC.md`, or have it
generate an `AGENTS.md` from them for whatever tool you use. `/meditate` is a
convenience that encodes the run order; `scripts/ingest --help` is the same
procedure without it.

### If you are not on an Apple Silicon Mac

One optional feature is Mac-only: `scripts/transcribe`, which turns audio into
a transcript locally, uses `mlx-whisper` (Apple Silicon wheels only). Everything
else — ingestion, validation, generation, semantic search — is portable.

Two consequences:

- **Bring your own transcripts.** Put a `.md` transcript in `inbox/` instead of
  audio and the rest of the pipeline is unchanged. Any transcription service
  works; the agent will normalize the formatting when it stages the file.
- **Don't run `scripts/setup --ml`** — it installs transcription and search in
  one `pip` command, so it fails as a unit and you lose search too, which would
  otherwise have worked. Install search directly instead:

  ```
  python3 -m venv .venv && ./.venv/bin/pip install sentence-transformers
  ```

If you would rather have a native transcription path, this is a good first
thing to hand to your agent: `scripts/transcribe` is ~110 lines with one clearly
isolated model call, and swapping `mlx-whisper` for `faster-whisper` or a
hosted API is a contained change.

## Quick start

```
scripts/setup              # activate the pre-commit hook
scripts/setup --ml         # optional, Apple Silicon: transcription + search
scripts/fetch-bsb          # install the public-domain Berean Standard Bible
```

Then, before ingesting anything:

**1. Fill in `HERMENEUTICS.md`.** It ships as a skeleton on purpose. It is the
interpretive charter the agent reads before writing every entry — how you
determine meaning, what you hold doctrinally, how to handle a source that
disagrees with you. `examples/HERMENEUTICS.reformed-evangelical.md` is one
filled-in charter, included as an example of the *form*, not as a default. The
agent is instructed to stop and ask if it finds the skeleton unfilled.

**2. Put a file in `inbox/`** — a sermon recording, a transcript, an article, or
your own notes.

**3. Run `/meditate`** in Claude Code.

## Using it

### Ingesting a source

`/meditate` is a conversation, not a black box. It will:

1. **Transcribe** the audio, if you dropped audio, then delete the recording —
   the transcript is the artifact that gets kept.
2. **Check for duplicates** by content hash, so re-dropping a file you already
   ingested stops rather than doubling it.
3. **Ask you for anything it can't infer.** It reads the transcript for speaker,
   venue, date, series and passages, and asks about the rest instead of
   guessing. Dates are the usual gap.
4. **Write the entries** — the one step that needs judgment.
5. **Validate, regenerate, reindex**, and report what it wrote: sections filled,
   sections judged absent, questions raised.
6. **Show you the diff** and wait. It does not commit without your go-ahead.

A first ingestion of an hour-long sermon typically produces 40–60 entries and
takes a few minutes, most of it transcription.

### The six categories

Every entry lands in one of six sections. This is the vocabulary you'll be
reviewing, so it's worth knowing what belongs where:

| section | holds |
|---|---|
| **Exegesis** | what the text means — grammar, structure, the argument being made |
| **Application** | what it means for ordinary life, derived from the text rather than bolted on |
| **History** | background, cultural and grammatical context, how the passage has been received |
| **Doctrine** | how the text connects to systematic theology |
| **Illustrations** | the images, stories and analogies a speaker used |
| **Questions** | tensions, gaps, unresolved claims, and garbled transcript regions |

**Exegesis and Application entries must carry a verse key**; the other four may
omit one, since an illustration or a historical note is not always about a
specific verse. A section the agent judges genuinely absent from a source is
recorded in `sections_absent` — judging is not optional, so silence is always
deliberate.

The **Questions** section is the one people underestimate. It is where the agent
records that a speaker asserted something without arguing it, that two sources
conflict, or that the transcript is garbled at ¶136 and needs your ear. It turns
into a worklist rather than a pile of unnoticed problems.

### Writing your own notes

Not everything comes from someone else. To record your own study, add a page in
`notes/` — either by hand or by asking the agent:

```markdown
---
type: note
title: Two kinds of judgment in the church
medium: own-notes
date: 2026-07-27
passages: ["1 Corinthians 4:3-5"]
passage_keys: [1CO.4.3-5]
tags: [ecclesiology]
---

Why Paul can forbid judgment and Scripture can command discernment.

## Exegesis

- `[1CO.4.3-5]` "Judgment" here is not one act but two: the ultimate verdict,
  which Paul defers to the Lord's coming, and the ordinary discernment believers
  owe one another, which he never withdraws
```

`medium: own-notes` is what tells the tools these are your words, which is why
anchors are optional here — there is no one else's text to stay faithful to. On
a page about someone else's material, anchors are required. Note pages flow into
the verse tree exactly like sermon pages, so your own conclusions sit beside the
sermons on the same verse.

**About tags.** The first time you use a tag, `scripts/validate` warns that it
has no topic page:

```
WARN: tag 'ecclesiology' has no topics/ecclesiology.md page
```

That is a nudge, not a failure — it is asking you to say in a sentence or two
what you mean by the tag, in `topics/ecclesiology.md`. Backlinks to everything
carrying it are generated for you in `topics/_generated/`. Write the page or
drop the tag; both make the warning go away, and the warning exists to stop a
vocabulary of near-duplicate tags accumulating unnoticed.

### Asking your corpus questions

Mostly you just ask, in Claude Code: *"what do my sources say about Mark 4?"*,
*"has anyone I've listened to addressed assurance?"*, *"where do Busenitz and
Holland disagree?"* The agent uses the three tools below. They're worth knowing
because you can also use them directly.

**1. Read the verse tree.** This is the primary surface. Verse pages exist only
where notes exist, so the file listing is itself an answer to "what have I
studied here?"

```
ls scripture/mark/004/          # 003.md 005.md 013.md index.md → v3, v5, v13 have notes
cat scripture/mark/004/003.md   # the verse, its notes by category, cross-references
cat scripture/mark/index.md     # every chapter, with note counts
```

**2. Expand a range, then grep.** For verse-precise or cross-chapter work.
Passage keys overlap — a note keyed `ROM.8.28-39` will not be found by grepping
for `ROM.8.30` — so expand the range first and search the expanded keys rather
than the range string:

```
scripts/passage-key --expand "Mark 4:1-10"     # → MRK.4.1 MRK.4.2 … MRK.4.10
grep -rl "MRK.4.3" sermons/ notes/ resources/
```

**3. Search semantically.** For concepts rather than references — finding the
sermon about suffering that never uses the word "suffering":

```
scripts/search --reindex                # after ingesting; incremental
scripts/search "enduring trials without understanding why"
scripts/search "union with Christ" -k 15
```

The index is local (`bge-small` embeddings, gitignored, rebuildable) and needs
the optional ML dependencies. `scripts/search` also prints the structural
equivalent when your query looks like a reference, so the two modes compose.

**Also generated for you:** `speakers/<name>.md` and `series/<name>.md` list
everything by source, `topics/_generated/<tag>.md` gives tag backlinks, and
`INDEX.md` carries corpus health — open questions, tags without topic pages,
verses cited but missing text.

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
hand-edit it. `scripts/validate` errors if you do, because the next
`scripts/generate` would silently delete your edit.

## Scripts

| | |
|---|---|
| `scripts/setup` | git hooks; `--ml` installs transcription + search deps |
| `scripts/fetch-bsb` | install the public-domain BSB into the text store |
| `scripts/transcribe` | local audio → paragraph transcript (Apple Silicon) |
| `scripts/ingest` | the deterministic ingestion pipeline (SPEC §9) |
| `scripts/validate` | read-only conformance checks; run by the pre-commit hook |
| `scripts/generate` | rebuild every generated page, deterministically |
| `scripts/search` | fully local semantic index (no API keys, no server) |
| `scripts/passage-key` | convert and expand passage references |

Every script takes `--help`, exits 0 on success and 1 on errors, and treats
`--strict` as "promote warnings to errors."

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

## Where the design is written down

- **`SPEC.md`** — normative. Frontmatter grammar, passage keys, entry lines and
  anchors, filename slugs, the text store, the generated tree, the ingestion
  pipeline, the format version. If any other document disagrees with SPEC, SPEC
  wins.
- **`CLAUDE.md`** — how the agent operates: safety rules, the ingestion
  workflow, the retrieval workflow.
- **`HERMENEUTICS.md`** — yours to write.

## Stability

**Pre-1.0 — the mechanics are still moving.** Below `1.0.0` the MINOR version
is the compatibility axis: `0.1.x` → `0.2.0` may require migrating an existing
corpus, `0.1.0` → `0.1.7` will not.

Your corpus records the format it was built against in `.iona-version`, and
`scripts/validate` — which the pre-commit hook runs — warns whenever that
disagrees with the scripts. So you find out you are behind at your next commit,
rather than by having to watch this repository.

To upgrade: replace `scripts/`, `SPEC.md`, `templates/` and `.claude/`, follow
[`MIGRATIONS.md`](MIGRATIONS.md) for each minor version crossed, then update
`.iona-version`. Never replace `HERMENEUTICS.md` or your content directories.
See [`CHANGELOG.md`](CHANGELOG.md) for what changed, and SPEC §10 for the rule.

1.0 comes when the format has held steady through real use — including by
someone other than the author, since that is the only way to learn which
mechanics are actually load-bearing.

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
