# sources/sync-backup/bup/lib/bup/cmd/damage.py

## Purpose
`damage.py` is a deliberately destructive testing command that corrupts byte ranges in one or more files. It is intended for recovery/fsck testing, not normal repository operation.

## APIs and Control Flow
The only helper is `randblock(n)`, which returns `n` pseudo-random bytes. `main(argv)` parses `--num`, `--size`, `--percent`, `--equal`, and `--seed`, then opens each target in `r+b`, computes a maximum corruption size, and writes random blocks either at random offsets or evenly spaced offsets. Input paths are normalized through `argv_bytes`; progress is logged with `path_msg`.

## State, Dependencies, Integration, Risks, Tests
The command mutates files in place and has no rollback. `--seed` makes corruption repeatable for tests. Empty files are risky because offset math assumes a positive size; large `--percent`/`--size` settings can overwrite most or all content. It integrates with `bup fsck` and parity-data tests by creating damaged pack or index files. Test signals are deterministic seed behavior, correct size/offset bounds, and refusal to run without filenames.
