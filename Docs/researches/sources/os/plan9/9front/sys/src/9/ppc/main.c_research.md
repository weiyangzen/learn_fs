# File Research: sources/os/plan9/9front/sys/src/9/ppc/main.c

PowerPC kernel bootstrap and configuration parsing.

Key responsibilities:
- Identifies supported PPC CPU types and prints CPU frequency information.
- `main()` zeros BSS, initializes machine state, memory config, xalloc, traps, MMU, plan9.ini parsing, interrupts, clock/timer, console/print, processes, segments, devices, pages, shared segments, FP state, first user process, and scheduler.
- Parses `plan9ini` text into name/value entries and implements `getconf()`.
- `init0()` initializes devices, sets core environment variables and plan9.ini variables, starts alarm and MMU sweep kernel processes, and enters user mode.
- Implements process FP setup/save hooks and memory sizing in `confinit()`.
- Parses ISA-style config strings into `ISAConf`.
- Rejects hardware watchpoint requests.

Dependencies:
- Orchestrates most PPC port subsystems plus shared Plan 9 kernel initialization.

Notable behavior:
- Memory configuration is Blast-board-specific: memory begins after the kernel image in `MEM1`, with optional `MEM2`.
