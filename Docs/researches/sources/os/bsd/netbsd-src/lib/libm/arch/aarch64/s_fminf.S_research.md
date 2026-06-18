# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fminf.S

- Role: `aarch64` minimum routine for `s_fminf`.
- Key behavior: returns the floating-point minimum using native min/max instruction support.
- Interfaces: exports/aliases `fminf -> _fminf, _fminf` and uses AArch64 scalar FP instructions and `machine/asm.h`/`aarch64/asm.h` entry macros.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `41` lines, `1742` bytes read from the source file.
