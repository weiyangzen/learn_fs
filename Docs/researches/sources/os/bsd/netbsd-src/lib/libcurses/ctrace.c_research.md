# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ctrace.c

Read completely: 109 lines.

This file provides debug-only tracing when `DEBUG` is defined. `__CTRACE_init` reads `CURSES_TRACE_MASK` and `CURSES_TRACE_FILE`, supports negative masks as exclusions from `__CTRACE_ALL`, opens the trace file unless set to `<none>`, and records initialization. `__CTRACE` lazily initializes tracing, filters by area mask, optionally prefixes timestamps, writes formatted output, tracks newline state, and flushes after every trace.

Non-debug builds define only a dummy typedef to avoid an empty translation unit; `__CTRACE` becomes a macro in `curses_private.h`.

Important interactions: trace areas are declared in `curses_private.h`. Many files in this group call `__CTRACE` throughout control paths.

Reliability notes: debug tracing opens the configured file with `"w"`, truncating existing content. The trace file is never explicitly closed.
