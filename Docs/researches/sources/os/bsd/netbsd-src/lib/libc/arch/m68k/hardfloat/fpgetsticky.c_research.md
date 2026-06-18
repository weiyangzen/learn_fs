# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetsticky.c

m68k hardfloat `fpgetsticky`.

Key points:
- Weak-aliases `fpgetsticky` to `_fpgetsticky`.
- Reads FPU status/control state.
- Returns sticky FP exception flags.
