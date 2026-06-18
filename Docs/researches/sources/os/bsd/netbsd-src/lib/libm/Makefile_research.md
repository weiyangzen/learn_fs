# File Research: sources/os/bsd/netbsd-src/lib/libm/Makefile

Top-level NetBSD `libm` build definition. It selects architecture-specific assembly/C sources for aarch64, alpha, arm, ia64, hppa, sparc, sparc64, i387/x86, m68k/m68060, vax, riscv, powerpc, mips, and sh3.

It builds `m.expsym`, sets IEEE/multi-libm flags, handles softfloat fenv fallbacks, substitutes arch assembly for common C sources, defines manual page links, and includes complex/compiler_rt/generated libm fragments.
