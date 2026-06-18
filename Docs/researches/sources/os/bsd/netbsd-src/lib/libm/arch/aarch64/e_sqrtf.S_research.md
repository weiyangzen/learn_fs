# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrtf.S

- Role: `aarch64` square-root routine for `e_sqrtf`.
- Key behavior: computes square root using the architecture FP sqrt instruction or FPSP wrapper.
- Interfaces: exports/aliases `__ieee754_sqrtf` and uses AArch64 scalar FP instructions and `machine/asm.h`/`aarch64/asm.h` entry macros.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `39` lines, `1730` bytes read from the source file.
