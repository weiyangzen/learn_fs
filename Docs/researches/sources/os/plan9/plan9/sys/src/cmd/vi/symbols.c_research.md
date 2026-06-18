# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/symbols.c

Purpose: Source and stack-symbol support for the MIPS simulator.

Key behavior:
- `printsource` prints `file:line` for an address.
- `printlocals` and `printparams` use local symbol metadata to print frame locals and parameters.
- `stktrace` walks stack frames using `.frame` symbols, prints calls, source locations, and optionally locals.

Dependencies:
- Uses Plan 9 `mach` symbol APIs, simulated memory reads, register state, and debugger output.

Notable details:
- Stack traces stop at `_main` or after 40 frames.
