# sources/sync-backup/borg/docs/usage/analyze.rst.inc

Purpose: generated CLI reference for `borg analyze`, used to identify high-activity directories across selected archives.

Important APIs and control flow: exposes archive filters (`--match-archives`, `--sort-by`, `--first`, `--last`, age-window options). The described command iterates matching archives, then contained files, then chunk IDs and plaintext sizes, aggregating added and removed chunk sizes by direct parent directory.

State and persistence: read-only analysis of repository metadata and archive contents. It does not mutate archives or caches beyond ordinary read-side access.

Dependencies and integration points: generated from Borg's argparse/jsonargparse help and tied to archive matching semantics documented in `borg help match-archives`. Suggested remediation integrates with future `borg create` excludes or `borg recreate`.

Risks: analysis uses plaintext chunk sizes, not compressed repository sizes, so output is a usage signal rather than exact disk-space accounting. Archive filter mistakes can hide or overstate activity.

Test signals: generated docs should match parser help; command tests should verify filtered archive iteration and directory aggregation on known archive sequences.
