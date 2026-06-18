# File Research: sources/os/plan9/9front/sys/src/cmd/5i/symbols.c

This file provides source-location printing, local/parameter display, and stack tracing for `5i`.

Key elements:
- `printsource()` maps a program counter to `file:line` text via `fileline()`.
- `printlocals()` walks local symbols for a function and prints automatic variables read from the emulated stack frame.
- `printparams()` prints function parameters from the frame pointer, skipping the saved PC.
- `stktrace()` walks frames from emulated `PC` and `SP`, stopping at `_main` or after 40 frames.

Dependencies and integration:
- Uses libmach `Symbol` records and helpers such as `findsym()`, `findlocal()`, `localsym()`, `symoff()`, and `fileline()`.
- Reads emulated memory using `getmem_4()`.
- Called by branch tracing in `run.c` and profiling in `stats.c`.

Notable behavior:
- Stack unwinding depends on Plan 9 symbol metadata, especially `.frame`.
- Leaf functions or first-instruction PCs are handled specially using link register `R14`.
- With modifier `'C'`, `stktrace()` also prints locals.

Research notes:
- This is debugger-style support code, tightly coupled to Plan 9 symbol conventions and ARM stack-frame layout.
