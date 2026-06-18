# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/debug.h

Debug macro header for Antiword.

Important behavior:
- Under `DEBUG`, defines macros that print file, line, and values for messages, strings, chars, decimals, hex, floats, block dumps, Unicode dumps, and FIXME markers.
- Conditional forms such as `DBG_DEC_C` print only when a condition is true.
- Under non-debug builds, debug macros compile to empty statements.
- `NO_DBG_*` macros are always empty.
- Under `TRACE`, `TRACE_MSG()` emits short trace messages and flushes stderr.

Role:
- Provides compile-time diagnostics without runtime cost in release builds.
