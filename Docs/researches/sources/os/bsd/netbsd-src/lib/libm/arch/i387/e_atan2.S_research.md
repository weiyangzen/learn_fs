# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2.S

- Role: `i387` transcendental math routine for `e_atan2`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `__ieee754_atan2` and uses x87 instructions with i386/x86_64 ABI helpers from `abi.h` where needed.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `18` lines, `309` bytes read from the source file.
