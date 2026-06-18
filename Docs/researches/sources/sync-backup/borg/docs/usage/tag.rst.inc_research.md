# sources/sync-backup/borg/docs/usage/tag.rst.inc

Purpose: Documents `borg tag`, which manages archive tags used for matching and protection.

Important APIs/types/functions: CLI contract is `borg [common options] tag [options] [NAME]`. Mutators are `--set TAG`, `--add TAG`, and `--remove TAG`; archive filters select target archives.

Control flow: Runtime resolves one or more archives by name/filter, computes the new tag set by setting, adding, or removing tags, and writes updated archive metadata. Special tag rules are enforced.

State and persistence: Mutates archive metadata tags. User-defined tags cannot start with `@`; known special tag `@PROT` protects archives against deletion or pruning. Pre-existing special tags cannot be removed via `--set` unless explicitly retained.

Dependencies and integration points: Tags integrate with archive matching (`tags:` filters in manifest/archive listing), prune/delete protection behavior, and `repo-list` output.

Risks: Incorrect tag mutation can remove operational classification or protection. Special tag validation must prevent users from inventing reserved `@` tags while preserving known special tags.

Test signals: Cover set/add/remove, multi-archive filtering, user tag validation, `@PROT` preservation/removal rules, prune/delete protection, and repo-list/tag-filter output.
