# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/vi.c

Purpose: Main program and runtime setup for the Plan 9 MIPS interpreter/debugger.

Key behavior:
- Loads a MIPS executable or initializes from a live `/proc/<pid>` snapshot.
- Sets up text/data/bss/stack segment maps, symbols, initial stack/TOS, registers, and default floating constants.
- Provides process snapshot initialization from `/proc/<pid>/mem`, `/proc/<pid>/text`, and `/proc/<pid>/segment`.
- Implements fatal/error output, instruction tracing, register dumps, allocation wrappers, and 32x32-to-64 multiply helpers.

Dependencies:
- Uses Plan 9 `mach`, executable headers, proc files, memory helpers, command loop, and MIPS shared state.

Notable details:
- `reset` contains `for(i = 0; i > Nseg; i++)`, so the loop body never runs; segment page freeing appears ineffective.
