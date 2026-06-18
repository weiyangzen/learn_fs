# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sinh.S

- Role: `m68060` transcendental math routine for `e_sinh`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `__ieee754_sinh` and uses m68060 assembly wrappers around FPSP/FPLSP offset entry points.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `24` lines, `516` bytes read from the source file.
