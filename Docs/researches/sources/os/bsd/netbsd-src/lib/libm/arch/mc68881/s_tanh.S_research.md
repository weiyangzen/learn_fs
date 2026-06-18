# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_tanh.S

- Role: `mc68881` transcendental math routine for `s_tanh`.
- Key behavior: uses x87/m68k FP instructions or m68060 FPSP wrapper calls for the named elementary function.
- Interfaces: exports/aliases `tanh` and uses Motorola 68881 FP instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `50` lines, `2079` bytes read from the source file.
