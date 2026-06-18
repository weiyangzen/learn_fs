# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/debug.h

This header defines Antiword’s debug and trace macros.

Key behavior:
- Under `DEBUG`, emits file/line-tagged messages, strings, chars, decimal/hex/float values, fixme markers, block dumps, and Unicode dumps.
- Under non-debug builds, expands those macros to empty statements.
- Provides conditional debug variants and explicit `NO_DBG_*` macros that are always empty.
- Under `TRACE`, emits trace messages and flushes stderr.

Important details:
- Debug macros use `stderr` directly and rely on helper functions declared elsewhere for block/Unicode dumps.
- This is compile-time instrumentation only.

Filesystem relevance:
- Indirect: helps inspect parsing and storage-mapping behavior during Antiword debugging.
