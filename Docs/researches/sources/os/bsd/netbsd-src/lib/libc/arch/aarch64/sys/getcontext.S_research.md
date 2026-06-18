# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/getcontext.S

AArch64 wrapper for `getcontext`.

Key behavior:
- Provides weak `getcontext` alias to `_getcontext`.
- Saves the user `ucontext_t *` argument in `x9`.
- Calls the `getcontext` syscall and error handler.
- Stores the link register as the saved program counter in the ucontext.
- Stores zero into saved `x0` so resumed context returns zero.
- Returns zero.

Dependencies:
- `assym.h` offsets `_UC_REGS_PC` and `_UC_REGS_X0`.
- Kernel `getcontext` syscall.

Notes:
- Contains a placeholder comment for softfloat exception/rounding state.
