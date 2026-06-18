# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_dump.c

Read completely: 533 lines.

## Purpose
Implements generic kernel crash dump writing, full-memory ELF core dump generation, buffered dump I/O helpers, and optional minidump/live-dump plumbing.

## Main Elements
- Builds generic physical memory dump maps from `dump_avail` through `dumpsys_gen_pa_init()` and iterates them with `dumpsys_gen_pa_next()`.
- Provides weak/generic machine hooks for cache writeback, chunk unmap, and auxiliary headers.
- Implements block-buffered dump helpers: `dumpsys_buf_seek()`, `dumpsys_buf_write()`, and `dumpsys_buf_flush()`.
- Dumps physical memory ranges in chunks via `dumpsys_cb_dumpdata()`, respecting dumper max I/O size, watchdog patting, progress output, and console Ctrl-C abort.
- Builds full ELF core headers in `dumpsys_generic()`, including ELF header, `PT_LOAD` program headers, auxiliary headers, page-aligned segment offsets, dump start/finish headers, and common failure messages.
- When `MINIDUMP_PAGE_TRACKING` is enabled, tracks minidump progress and implements `minidumpsys()` for panic dumps and best-effort live dumps.
- Live dumps snapshot the message buffer and page dump bitset, but intentionally do not snapshot all mutable kernel state.

## Dependencies And Integration
Depends on dumperinfo backends, VM physical page metadata, machine dump hooks, ELF definitions, watchdog, console input, message buffer code, and architecture-specific `cpu_minidumpsys()`.

## Risk Notes
Dump paths run in failure or live diagnostic contexts, so they avoid complex recovery. Live dumps are explicitly best-effort and may contain inconsistent kernel state. Buffered writes must preserve block alignment and flush ordering.
