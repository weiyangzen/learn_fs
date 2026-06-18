# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.c

This file implements Antiword’s custom assertion failure handler.

Key behavior:
- In non-`NDEBUG` builds, `__fail()` validates its arguments, optionally prints a debug message, and terminates through `werr(1, ...)`.
- Reports the failed expression, source file, and line number.

Important details:
- The function is compiled only when assertions are enabled.
- Runtime behavior depends on `werr()` for fatal reporting.

Filesystem relevance:
- Indirect: assertion support for document parsing and conversion code.
