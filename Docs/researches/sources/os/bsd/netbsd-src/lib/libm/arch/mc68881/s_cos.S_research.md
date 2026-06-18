# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_cos.S

- Role: `mc68881` transcendental math routine for `s_cos`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `cos -> _cos, _cos` and uses Motorola 68881 FP instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `53` lines, `2123` bytes read from the source file.
