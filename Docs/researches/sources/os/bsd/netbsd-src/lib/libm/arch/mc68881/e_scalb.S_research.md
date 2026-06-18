# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_scalb.S

- Role: `mc68881` scaling routine for `e_scalb`.
- Key behavior: scales the significand by a power of two using native scale instructions.
- Interfaces: exports/aliases `__ieee754_scalb` and uses Motorola 68881 FP instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `20` lines, `379` bytes read from the source file.
