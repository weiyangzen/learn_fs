# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fabsf.S

- Role: `aarch64` absolute-value routine for `s_fabsf`.
- Key behavior: clears the sign bit using the architecture FP absolute-value/sign instruction.
- Interfaces: exports/aliases `fabsf` and uses AArch64 scalar FP instructions and `machine/asm.h`/`aarch64/asm.h` entry macros.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `39` lines, `1709` bytes read from the source file.
