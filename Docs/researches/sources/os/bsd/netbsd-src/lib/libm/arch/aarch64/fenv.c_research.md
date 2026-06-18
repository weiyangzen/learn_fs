# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/fenv.c

AArch64 floating-point environment implementation. It reads/writes `FPSR` and `FPCR` to implement exception flags, rounding mode, environment save/restore, hold/update, and exception enable masks.

Defines `__fe_dfl_env` with round-to-nearest. Several `_DIAGASSERT` checks reference `except` where `excepts` appears intended.
