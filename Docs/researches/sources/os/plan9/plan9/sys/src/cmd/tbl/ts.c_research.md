# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/ts.c

Small string and numeric utility functions for `tbl`.

Functions:
- `match` for exact string equality.
- `prefix` for prefix testing.
- `letter`, `digit` character predicates.
- `numb` decimal integer conversion.
- `max`.
- `tcopy` string copy.

These are local replacements for simple libc-style operations, matching the historical source style.
