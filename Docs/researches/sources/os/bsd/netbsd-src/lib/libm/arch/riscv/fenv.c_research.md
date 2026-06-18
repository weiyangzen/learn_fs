# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/fenv.c

RISC-V fenv implementation. It manipulates `fcsr`, `fflags`, and `frm` CSR fields for exception flags, rounding mode, environment save/restore, and update.

`fesetround()` validates against `FCSR_FRM_RMM`; `fesetenv()` rejects unknown bits. Exception enable/disable extension functions are stubs returning zero.
