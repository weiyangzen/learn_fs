# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmin.S

RISC-V double `fmin` implementation. It uses `fmin.d fa0, fa0, fa1`; `fminl` is a strong alias when long double is not distinct.
