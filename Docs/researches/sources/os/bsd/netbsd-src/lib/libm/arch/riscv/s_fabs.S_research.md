# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabs.S

- Role: `riscv` absolute-value routine for `s_fabs`.
- Key behavior: clears the sign bit using the architecture FP absolute-value/sign instruction.
- Interfaces: exports/aliases `fabs` and uses RISC-V F/D floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `191` bytes read from the source file.
