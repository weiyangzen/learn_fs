# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t.h

`t.h` is the shared header for the Plan 9 `tbl` troff preprocessor implementation.

Contents:
- Includes `<u.h>`, `<libc.h>`, `<bio.h>`, and `<ctype.h>`.
- Defines table sizing constants: max lines, header/spec rows, columns, character storage, line length, repeats, and column width string length.
- Declares global table parser/rendering state: row/column counts, styles, fonts, sizes, vertical sizes, flags, lines, table cells, storage arenas, active input/output buffers, file/line tracking, and formatting flags.
- Defines style/flag constants such as `ZEROW`, `HALFUP`, `CTOP`, `CDOWN`, column alignment constants, register numbers, and line-position constants.
- Declares `struct colstr` for split table cell storage.
- Provides prototypes for all tbl compilation units from `t1.c` through later helper files (`t8.c`, `t9.c`, `tb.c`, etc.).

Role:
- This header is the cross-file contract for a highly global, historical C program. Most state is shared mutable global data rather than passed explicitly.

Risks:
- Many extern globals and macro constants make ordering and memory ownership fragile.
- `MAXCOL` warning notes it must stay coordinated with register allocation in `tr.c`.
