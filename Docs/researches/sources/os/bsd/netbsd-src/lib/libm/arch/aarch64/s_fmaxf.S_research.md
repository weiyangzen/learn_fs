# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaxf.S

- Role: `aarch64` maximum routine for `s_fmaxf`.
- Key behavior: returns the floating-point maximum using native max instruction support.
- Interfaces: exports/aliases `fmaxf -> _fmaxf, _fmaxf` and uses AArch64 scalar FP instructions and `machine/asm.h`/`aarch64/asm.h` entry macros.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `41` lines, `1742` bytes read from the source file.
