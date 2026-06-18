# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspenum.h

Defines common client-facing path enumeration symbols.

Key definitions:
- Path element IDs: `gs_pe_moveto`, `gs_pe_lineto`, `gs_pe_curveto`, `gs_pe_closepath`.
- Opaque `gs_path_enum` type.

Integration:
- Included by `gspath.h`.
- Used by path enumeration APIs implemented in `gspath1.c`.

Risk notes:
- Simple constant header; consumers must match the point-count contract for each path element type.
