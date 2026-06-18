# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.c

Merge regression fixture with deletions.

Key behavior:
- Contains `1`, `2`, `4`, `5`, `6`, `8`, `9`, `10`.
- Omits `3` and `7` relative to the 1-10 baseline.

Research notes:
- Paired with `merge-t2.l`, which restores/includes `3` but still omits `7`.
