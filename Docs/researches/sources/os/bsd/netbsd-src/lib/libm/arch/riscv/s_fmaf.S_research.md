# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaf.S

RISC-V single-precision fused multiply-add implementation. The entry point is named `fmaddf` and uses `fmadd.s fa0, fa0, fa1, fa2`.
