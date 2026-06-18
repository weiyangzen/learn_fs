# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/getcontext.S

Alpha wrapper for `getcontext`.

Key behavior:
- Provides weak `getcontext` alias to `_getcontext`.
- Calls kernel `getcontext`.
- Stores `ra` into the saved PC slot of the ucontext.
- Stores zero into the saved `v0` slot so resumed context returns zero.
- Returns to caller.

Dependencies:
- `assym.h` offsets for `UC_GREGS`, `_REG_PC`, and `_REG_V0`.
