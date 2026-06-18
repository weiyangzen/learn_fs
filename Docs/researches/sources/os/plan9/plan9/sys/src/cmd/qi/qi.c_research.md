# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/qi.c

Program loader, process snapshot loader, stack initializer, and utility routines for the `qi` emulator/debugger.

Key responsibilities:
- Opens a PowerPC executable or attaches to a numeric `/proc` pid snapshot.
- Reads and validates executable headers with libmach, initializes symbols and maps.
- Builds text/data/BSS/stack segment tables and instruction profiling storage.
- Reads live process segments and selected registers from `/proc`.
- Resets register/memory state and breakpoint pass counts.
- Builds an initial Plan 9 user stack and `Tos` area with argv and pid.
- Provides fatal/error reporting, instruction tracing, register dumps, floating dumps, and zeroing allocators.

Dependencies:
- Uses libmach `Fhdr`, maps, symbols, Plan 9 `/proc`, `power.h`, `mem.c`, and `cmd.c`.

Notable risks:
- `reset()` has a loop condition `i > Nseg`, so segment cleanup never runs.
- `procinit()` reads `roff[i-1]` starting at `i=0`, which indexes before the register-offset array.
- Stack/Tos construction embeds 32-bit PowerPC and Plan 9 layout assumptions.
