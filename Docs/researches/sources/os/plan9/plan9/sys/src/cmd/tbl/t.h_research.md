# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t.h

Central header for the Plan 9 `tbl` troff table preprocessor.

Contents:
- Global limits such as `MAXLIN`, `MAXHEAD`, `MAXCOL`, `MAXCHS`, and `CLLEN`.
- Shared global state for table dimensions, parsed styles, fonts, sizes, flags, spans, line drawing, input buffers, and output `Biobuf`.
- Style/flag constants such as `ZEROW`, `HALFUP`, `CTOP`, `CDOWN`, and line direction constants.
- Troff register constants (`S1`, `S2`, `TMP`, `LSIZE`, etc.).
- Function prototypes grouped by source module from `t1.c` through `tv.c`.

Architectural role:
- `tbl` is implemented as many small C files sharing global arrays allocated per table. This header is the single cross-module contract.
- `MAXCOL` is tied to register allocation in `tr.c`; increasing it requires extending `nregs[]`.
