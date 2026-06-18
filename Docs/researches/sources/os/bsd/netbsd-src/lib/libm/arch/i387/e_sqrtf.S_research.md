# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrtf.S

- Role: `i387` square-root routine for `e_sqrtf`.
- Key behavior: computes square root using the architecture FP sqrt instruction or FPSP wrapper.
- Interfaces: exports/aliases `__ieee754_sqrtf` and uses x87 instructions with i386/x86_64 ABI helpers from `abi.h` where needed.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `17` lines, `261` bytes read from the source file.
