# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/ext.h

Global external declarations for the troff/nroff program.

Key responsibilities:
- Declares shared state for input stacks, buffers, page ranges, diversions, environments, number registers, macro state, output state, fonts, terminal tables, special character ids, and DWB path strings.
- Exposes the central indirect function pointers that switch behavior between troff and nroff back ends.
- Bridges definitions from files such as `ni.c`, `n1.c`, `n2.c`, `n3.c`, `n4.c`, `n5.c`, `n7.c`, `n10.c`, and troff-specific `t*.c` files.

Important behavior:
- This header is a shared-state contract, not an abstraction boundary.
- Many globals are updated by multiple subsystems during input parsing, layout, and output.
- Historical names and declarations include state used only by troff or only by nroff.

Notable risks:
- Type and storage mismatches across old C files would produce subtle corruption.
- The program architecture relies heavily on global mutable state and indirect function variables.
