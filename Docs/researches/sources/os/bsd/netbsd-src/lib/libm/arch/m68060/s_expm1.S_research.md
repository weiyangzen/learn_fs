# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1.S

- Role: `m68060` transcendental math routine for `s_expm1`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `expm1 -> _expm1, _expm1` and uses m68060 assembly wrappers around FPSP/FPLSP offset entry points.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `26` lines, `519` bytes read from the source file.
