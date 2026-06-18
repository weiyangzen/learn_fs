# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/symbols.c

Symbol, source, and stack-trace support for `qi`.

Key responsibilities:
- Prints file:line information for a program counter.
- Prints local variables and parameters using libmach symbol metadata and simulated stack memory.
- Walks stack frames from current PC/SP using `.frame` symbols and saved return PCs.
- Handles leaf/local function cases and stops at `_main`.
- Optionally prints locals for `$C` stack traces.

Dependencies:
- Uses libmach symbol APIs, `mach->szreg`, simulated memory access, and current register state.

Notable risks:
- Stack walking depends on correct `.frame` metadata and PowerPC frame layout.
- Local/parameter printing reads fixed 4-byte values and may not represent larger or floating types correctly.
- Trace is truncated after 40 frames.
