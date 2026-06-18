# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t11.l

Merge regression fixture with boundary insertions and middle replacement.

Key behavior:
- Adds `A` before `1` and `Z` after `10`.
- Replaces line `5` with `y`.

Research notes:
- Exercises merge handling at file start, file end, and an interior change in one fixture.
