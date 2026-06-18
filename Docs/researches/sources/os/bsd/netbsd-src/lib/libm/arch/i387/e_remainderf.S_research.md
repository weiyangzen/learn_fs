# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainderf.S

- Role: `i387` remainder routine for `e_remainderf`.
- Key behavior: computes FP remainder/modulus using native remainder instructions or loops until the FP status reports completion.
- Interfaces: exports/aliases `__ieee754_remainderf` and uses x87 instructions with i386/x86_64 ABI helpers from `abi.h` where needed.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `22` lines, `361` bytes read from the source file.
