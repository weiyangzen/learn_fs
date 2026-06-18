# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fma.S

- Role: `riscv` fused multiply-add routine for `s_fma`.
- Key behavior: computes `(x * y) + z` with a fused multiply-add instruction where the ISA provides one.
- Interfaces: exports/aliases `fma` and uses RISC-V F/D floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `199` bytes read from the source file.
