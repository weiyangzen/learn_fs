# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tb.c

Usage analysis and pooled allocation helpers for `tbl`.

Key functions:
- `checkuse` marks which columns have visible left, right, or split content.
- `real` determines whether a cell pointer represents actual printable content or a nonempty diversion.
- `chspace` allocates/reuses large character buffers.
- `alocv` allocates vector storage from pooled `MAXCHS` blocks and zeroes it.
- `release` resets pool cursors and text split storage.

Notable behavior:
- Comments preserve historical reluctance to `free` vector pools, but the implementation reuses pools by resetting counters.
- `MAXVEC` and `MAXPC` cap temporary character and vector pools.
