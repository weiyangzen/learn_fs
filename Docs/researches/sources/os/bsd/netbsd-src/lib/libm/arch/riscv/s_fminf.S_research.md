# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fminf.S

- Role: `riscv` minimum routine for `s_fminf`.
- Key behavior: returns the floating-point minimum using native min/max instruction support.
- Interfaces: exports/aliases `fminf` and uses RISC-V F/D floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `199` bytes read from the source file.
