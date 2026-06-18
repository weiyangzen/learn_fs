# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_logf.S

- Role: `m68060` transcendental math routine for `e_logf`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `__ieee754_logf` and uses m68060 assembly wrappers around FPSP/FPLSP offset entry points.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `22` lines, `478` bytes read from the source file.
