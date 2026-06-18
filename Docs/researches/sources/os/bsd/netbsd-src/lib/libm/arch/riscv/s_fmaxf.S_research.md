# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaxf.S

- Role: `riscv` maximum routine for `s_fmaxf`.
- Key behavior: returns the floating-point maximum using native max instruction support.
- Interfaces: exports/aliases `fmaxf` and uses RISC-V F/D floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `199` bytes read from the source file.
