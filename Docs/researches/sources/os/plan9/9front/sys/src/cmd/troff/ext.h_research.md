# File Research: sources/os/plan9/9front/sys/src/cmd/troff/ext.h

Read completely: 184 lines, 3497 bytes.

Global extern declaration header for the troff/nroff program. It exposes shared process state across the historically split `n*.c` and `t*.c` translation units.

Key contents:
- Input/output buffers, file stacks, macro/string storage offsets, diversion state, environments, registers, traps, page ranges, fonts, special character names, terminal paths, and flags.
- Externs for `Numtab *numtabp`, `Diver *dip`, `Stack` frames, `Wcache`, translation table, and special-character integer IDs.
- DWB pathname globals: `DWBfontdir`, `DWBntermdir`, and `DWBalthyphens`.

Dependencies:
- Definitions are primarily in `ni.c`, with behavior spread across `n1.c` through `n10.c` and troff-specific files.

Reliability notes:
- This is a shared-state architecture; correctness depends on disciplined global mutation rather than encapsulation.
