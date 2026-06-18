# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1f.S

- Role: `m68060` transcendental math routine for `s_expm1f`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `expm1f -> _expm1f, _expm1f` and uses m68060 assembly wrappers around FPSP/FPLSP offset entry points.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `24` lines, `487` bytes read from the source file.
