# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tr.c

Allocates troff number register names for table columns.

Contents:
- `nregs[]` is a fixed list of two-character register names.
- `reg(col, place)` indexes into `nregs` based on `qcol * place + col`.

Notable behavior:
- Enforces that `nregs` has at least `3*qcol` entries.
- Supports left, center/mid, and right register sets via `CLEFT`, `CMID`, and `CRIGHT`.
- `MAXCOL` in `t.h` must stay compatible with this array.
