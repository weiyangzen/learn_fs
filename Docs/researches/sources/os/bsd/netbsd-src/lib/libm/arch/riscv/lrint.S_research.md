# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrint.S

RISC-V `lrint` for double input. It converts `fa0` to `a0` with `fcvt.l.d` on LP64 or `fcvt.w.d` otherwise; LP64_X aliases `llrint`.
