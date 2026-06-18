# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaf.S

- Role: `aarch64` fused multiply-add routine for `s_fmaf`.
- Key behavior: computes `(x * y) + z` with a fused multiply-add instruction where the ISA provides one.
- Interfaces: exports/aliases `fmaf -> _fmaf, _fmaf` and uses AArch64 scalar FP instructions and `machine/asm.h`/`aarch64/asm.h` entry macros.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `41` lines, `1741` bytes read from the source file.
