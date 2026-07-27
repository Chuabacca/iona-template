# HERMENEUTICS.md — the interpretive charter

**This file is a skeleton. Fill it in before your first ingestion.**

This charter governs how the agent categorizes, summarizes, and applies
scripture content. It shapes *how the agent writes*; it never overrides *what a
source actually said*.

Every tradition reads with commitments. The point of writing yours down is not
to make the corpus agree with you — §3 below exists precisely to stop that — but
to make the agent's choices predictable and inspectable instead of drifting
toward whatever the model absorbed in training. An unwritten charter is not a
neutral charter; it is an unexamined one.

`examples/HERMENEUTICS.reformed-evangelical.md` is one filled-in charter, from a
Grace Community Church / Master's Seminary / Reformed Evangelical position. It
is an example of the *form*, not a default. Copy it over this file if it is
genuinely yours; otherwise write your own using the headings below. Do not leave
this file as a skeleton — the agent reads it before writing every entry, and a
skeleton tells it nothing.

## 1. Interpretive method

State how meaning is determined. Be specific enough that the agent can tell
whether a given entry belongs in `## Exegesis` or `## Application`.

Questions worth answering here:

- Where does meaning live — authorial intent, the text itself, the reading
  community, the canon as a whole?
- One meaning with many applications, or multiple legitimate senses?
- How does the rest of Scripture bear on a difficult passage?
- What is the role of the original languages, and how should the agent record
  observations about them?
- What warrants a typological or figurative reading?

## 2. Doctrinal commitments

List the theological positions the agent should assume when organizing
`## Doctrine` entries and choosing vocabulary. Name your tradition, confession,
or statement of faith if you have one.

Be honest about contested points. If you hold a position loosely, say so — the
agent will hedge where you hedge, and that is the correct behavior.

## 3. Rules for the agent

**These rules are mechanics, not doctrine. Keep them whatever your tradition.**
They are what makes a tradition-specific charter safe to hold.

1. **Faithfulness over conformity.** When a source conflicts with this charter,
   record the source's view faithfully and flag the tension as a `question`
   entry — never silently harmonize, soften, or editorialize. The corpus is a
   record of what your sources said, not a record of what you wish they had said.
2. **Anchored paraphrase.** Every categorized entry cites the source (SPEC §4
   anchors). The charter shapes emphasis and vocabulary, not content.
3. **Application entries** answer: what does this text mean for ordinary life?
   Concrete and text-derived, never floating free of the passage.
4. **History entries** hold historical and cultural background, grammatical
   context, and the reception history of the text.
5. **Doctrine entries** connect the text to systematic theology, using the
   commitments in §2 as the organizing grid.
6. When summarizing teachers outside your tradition, represent them accurately
   and note the difference — the corpus is a record, not an echo chamber.
7. **Never exegete text you cannot read.** Garbled or unrecoverable transcript
   regions become `question` entries, never guesses.
