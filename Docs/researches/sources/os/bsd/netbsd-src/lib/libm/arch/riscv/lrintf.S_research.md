# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrintf.S

RISC-V `lrintf` implementation. It converts float `fa0` to a signed long-sized integer with `fcvt.l.s` on LP64 or `fcvt.w.s` otherwise; `llrintf` is aliased on LP64_X builds.
