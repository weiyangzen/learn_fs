# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.h

This header defines Antiword’s `fail()` assertion macro.

Key behavior:
- In `NDEBUG`, `fail(e)` compiles to a no-op.
- Otherwise, if expression `e` is true, it calls `__fail()` with expression text, file, and line.
- Declares `__fail()`.

Important details:
- The macro is inverted compared with standard `assert`: callers pass the failure condition.

Filesystem relevance:
- Indirect: defensive checks throughout document storage parsing and rendering paths.
