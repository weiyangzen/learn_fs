# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/gd_qnan.h

This header defines canonical quiet-NaN patterns for RISC-V gdtoa. Comments cite the RISC-V ISA canonical NaN rule: positive sign and only the quiet bit set in the significand.

It defines single, double, and long-double/quad word patterns in little-endian order. These constants are used when conversion code synthesizes NaN values.
