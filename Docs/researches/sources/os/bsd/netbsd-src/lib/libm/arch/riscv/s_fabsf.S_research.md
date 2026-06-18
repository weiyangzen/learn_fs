# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabsf.S

- Role: `riscv` absolute-value routine for `s_fabsf`.
- Key behavior: clears the sign bit using the architecture FP absolute-value/sign instruction.
- Interfaces: exports/aliases `fabsf` and uses RISC-V F/D floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `194` bytes read from the source file.
