# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_atanh.S

- Role: `mc68881` transcendental math routine for `e_atanh`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `__ieee754_atanh` and uses Motorola 68881 FP instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `50` lines, `2094` bytes read from the source file.
