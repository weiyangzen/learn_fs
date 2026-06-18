# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t13.c

Merge regression fixture with sparse/marker content.

Key behavior:
- Starts with `1`, then several blank lines, then `10`.
- Includes marker-like lines `###1` and `###0`.
- Contains a second block with `1`, `2`, `3`, `4`, `y`, `6`, `9`, `ZZZZZZZZ`, blank line, `9`, `B`.

Research notes:
- Designed to stress merge chunk alignment, blank-line handling, and marker-like data that must not be confused with conflict markers.
