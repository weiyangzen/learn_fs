# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_copysignf.S

- Role: `riscv` copysign routine for `s_copysignf`.
- Key behavior: returns the magnitude of the first argument with the sign of the second argument using bit/sign manipulation.
- Interfaces: exports/aliases `copysignf` and uses RISC-V F/D floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `212` bytes read from the source file.
