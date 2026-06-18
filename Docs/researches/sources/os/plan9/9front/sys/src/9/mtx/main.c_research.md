# File Research: sources/os/plan9/9front/sys/src/9/mtx/main.c

This is MTX PowerPC kernel bootstrap and configuration code. `main` clears BSS, initializes `Mach`, I/O, console, formatting, memory configuration, allocator, Raven bridge, traps, print, CPU ID, MMU, interrupts, clock, processes, segments, timers, links, channel devices, pages, FP initial state, user process, and scheduler.

`machinit` initializes CPU type, a temporary delay constant, enables caches, and marks CPU 0 active. `cpuidprint` identifies the 604e. A small static `plan9ini` provides `console=0` and `ether0=type=2114x`, consumed by `getconf`.

`init0` initializes channel devices, sets environment variables, starts `alarm` and `mmusweep` kprocs, and enters user mode. `confinit` sizes process, page, image, swap, interrupt allocation, and memory pools based on ROM-provided `memsize`, CPU-server status, and optional `*kernelpercent`.

It also implements FP process setup/save hooks, ISA config parsing, and a no-watchpoint implementation.

Filesystem relevance is high: this file initializes the device namespace, page allocator, image cache sizing, COW mode, and initial user process.

Notable risks: configuration is hardcoded rather than parsed from a full plan9.ini source; reboot is unimplemented; exit uses watchdog reset.
