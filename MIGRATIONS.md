# MIGRATIONS

How to move an existing corpus across a breaking format change.

A repository created from this template shares no git history with it, so there
is no merge to perform. Upgrading means **replacing the mechanics and migrating
your data**:

```
scripts/  SPEC.md  templates/  .claude/     replace wholesale — CLAUDE.md §2
                                            forbids editing these anyway
HERMENEUTICS.md  inbox/ sources/ sermons/   never replace — yours
notes/ resources/ studies/ topics/*.md
scripture/ speakers/ series/ INDEX.md       generated; rebuilt by scripts/generate
```

Then work through every section below whose version you are crossing, in order,
and finally write the new version into `.iona-version`.

`scripts/validate` warns on every commit until `.iona-version` matches the
`FORMAT_VERSION` in `scripts/lib.py`, so an unfinished migration is hard to
forget.

## Before you start

```
git status                 # commit or stash your work first
scripts/validate           # know which errors predate the upgrade
```

Migrations only ever touch the authored pages under `sermons/`, `notes/` and
`resources/` and the config files. The generated tree is never migrated — it is
deleted and rebuilt by `scripts/generate`, which is always safe to re-run.

## 0.1.0 — baseline

The first public release. There is nothing to migrate from; write `0.1.0` into
`.iona-version` and run:

```
scripts/setup
scripts/validate
scripts/generate
```

---

## Template for future entries

Each breaking release adds a section here in this shape. Keep them, so a corpus
several versions behind can be walked forward one step at a time.

```markdown
## 0.2.0 — <one line: what changed and why it breaks>

**Breaks:** <what fails validate before migrating, verbatim error if useful>

**Affects:** <which files — e.g. every page with a `medium:` field>

**Steps:**

1. <mechanical step, ideally a command that can be re-run safely>
2. ...
3. Run `scripts/validate` — expect 0 errors.
4. Run `scripts/generate`.
5. Write `0.2.0` into `.iona-version`.

**If you had customized <X>:** <what to re-apply>
```
