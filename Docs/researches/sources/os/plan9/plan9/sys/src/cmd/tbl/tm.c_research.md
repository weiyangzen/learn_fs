# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tm.c

Splits numeric table entries into left and right parts for decimal alignment.

Key functions:
- `maknew` finds a split point: explicit `\&`, decimal point outside equation delimiters, or last digit boundary. It stores the right part in `exstore`, terminates the left part in place, and returns the right part pointer.
- `ineqn` reports whether a position is inside text delimited by `delim1`/`delim2`.

Notable behavior:
- If a field has no numeric split point, `maknew` returns `0`.
- Split storage is allocated from `chspace` and reused through `exstore`.
