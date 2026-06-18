# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.l

Merge regression fixture with blank ranges and marker-like lines.

Key behavior:
- Starts with `1` through `4`, then `x6`, `7`, `8`, `9`.
- Contains a long run of blank lines.
- Includes `##3`, then `4` through `10`.

Research notes:
- Complements `merge-t13.c` for complex overlap/alignment tests.
