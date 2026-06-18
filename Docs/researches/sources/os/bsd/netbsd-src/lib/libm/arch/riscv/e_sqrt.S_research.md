# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/e_sqrt.S

- Role: `riscv` square-root routine for `e_sqrt`.
- Key behavior: computes square root using the architecture FP sqrt instruction or FPSP wrapper.
- Interfaces: exports/aliases `__ieee754_sqrt` and uses RISC-V F/D floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `212` bytes read from the source file.
