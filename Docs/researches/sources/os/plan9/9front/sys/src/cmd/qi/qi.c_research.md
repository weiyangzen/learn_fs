# File Research: sources/os/plan9/9front/sys/src/cmd/qi/qi.c

Main program and process/executable setup for `qi`.

Key responsibilities:
- `main` initializes buffered I/O, opens either a q.out file or a `/proc` process, loads headers, initializes stack/registers, and enters the debugger.
- `inithdr` reads/cracks executable headers, initializes symbols, and sets Power machdata.
- `initmap` creates text/data/bss/stack segment descriptors and instruction profiling storage.
- `procinit` imports an existing process’s text, segment layout, selected registers, memory pages, and stack from `/proc`.
- `reset` resets register and memory state.
- `initstk` builds a Plan 9-style initial user stack and Tos area.
- `dumpreg`, `dumpdreg`, `fatal`, `itrace`, `emalloc`, and `erealloc` provide utility/debug support.

Dependencies and coupling:
- Uses Plan 9 `mach` header parsing/symbol APIs, `/proc` files, `mem.c` page accessors, and `cmd.c` REPL.
- Establishes globals consumed by every simulator subsystem.

Notable behavior:
- `procinit` contains a likely indexing bug: loop `for(i = 0; i < 32; i++) reg.r[i] = greg(m, roff[i-1]);` reads `roff[-1]` for `i == 0`.
- `reset` loop condition `for(i = 0; i > Nseg; i++)` never runs, so segment pages are not freed as intended.
