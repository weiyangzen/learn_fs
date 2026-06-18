# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmax.S

RISC-V double `fmax` implementation. It uses `fmax.d fa0, fa0, fa1`; `fmaxl` is a strong alias when long double is not distinct.
