# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_atanf.S

- Role: `i387` transcendental math routine for `s_atanf`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `atanf -> _atanf, _atanf` and uses x87 instructions with i386/x86_64 ABI helpers from `abi.h` where needed.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `23` lines, `394` bytes read from the source file.
