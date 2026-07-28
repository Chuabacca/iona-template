# Changelog

Notable changes to the corpus format and the mechanics that read it.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [semver](https://semver.org/), with the pre-1.0 rule below.

**This project is pre-1.0.** Below `1.0.0` the MINOR is the compatibility
axis: `0.1.x` → `0.2.0` may break an existing corpus, `0.1.0` → `0.1.7` will
not. Every minor bump gets an entry in [`MIGRATIONS.md`](MIGRATIONS.md).

## [Unreleased]

## [0.1.0] — 2026-07-27

First public release. Baseline format; nothing to migrate from.

### Added

- **Per-verse storage.** Notes are authored in `sermons/`, `notes/`,
  `resources/` and projected by `scripts/generate` onto one markdown file per
  verse — `scripture/<book>/<CCC>/<VVV>.md` — grouped by category, alongside
  book and chapter indexes. Verse pages exist only where notes exist.
- **`scripts/ingest`** — the deterministic half of ingestion: content-hash
  dedupe and resume detection, pure path/slug/passage-key derivation,
  idempotent staging, a readiness gate, and the validate → generate → reindex →
  clear-inbox sequence. State is derived from the filesystem, never stored.
- **`/meditate` skill** — the operating procedure that drives `scripts/ingest`,
  leaving the agent one judgment step: writing anchored entries.
- **Quote anchors** — every entry cites a paragraph of its source and quotes it
  verbatim; `scripts/validate` re-checks the quote, so correcting a transcript
  names the entries it invalidated.
- **`medium` as a fidelity axis** — `transcript-asr`, `transcript-export`,
  `authored`, `own-notes`. Records how exactly the words are held, which is
  what decides whether anchoring is required.
- **Versioned scripture text store** — `scripture/_text/<version>/`, with a
  public-domain default installed by `scripts/fetch-bsb` and copyrighted
  translations gitignored by default.
- **Cross-references** from the openbible.info dataset, rendered on verse pages.
- **`scripts/search`** — a fully local semantic index; no API keys, no server.
- **`.iona-version`** and the compatibility check described in SPEC §10.

### Notes

- `HERMENEUTICS.md` ships as a skeleton by design. The charter shapes every
  entry the agent writes, so it has to be the owner's; one filled-in charter is
  included under `examples/` as a demonstration of form.

[Unreleased]: https://github.com/Chuabacca/iona-template/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Chuabacca/iona-template/releases/tag/v0.1.0
