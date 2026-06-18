# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t5.l

Merge regression fixture with insertion plus replacement.

Key behavior:
- Inserts `a`, `b`, `c` after `1`.
- Replaces baseline line `5` with `x`.
- Keeps remaining numeric context through `10`.

Research notes:
- Tests multi-line insertion close to a later replacement.
