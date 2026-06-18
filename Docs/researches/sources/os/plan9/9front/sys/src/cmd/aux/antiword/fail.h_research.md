# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fail.h

Header defining Antiword’s `fail()` macro.

Important behavior:
- Undefines any previous `fail`.
- In `NDEBUG` builds, `fail(e)` compiles to no-op.
- Otherwise, `fail(e)` calls `__fail(#e, __FILE__, __LINE__)` when expression `e` is true.
- Declares `__fail`.

Role:
- Provides a lightweight assertion mechanism used heavily throughout Antiword modules.
