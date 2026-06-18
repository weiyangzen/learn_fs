# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysignf.S

- Role: `alpha` copysign routine for `s_copysignf`.
- Key behavior: returns the magnitude of the first argument with the sign of the second argument using bit/sign manipulation.
- Interfaces: exports/aliases `s_copysignf` and uses Alpha FP/integer bit operations and `machine/asm.h` entry macros.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `37` lines, `1643` bytes read from the source file.
