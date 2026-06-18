# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fmaf.S

- Role: `powerpc` fused multiply-add routine for `s_fmaf`.
- Key behavior: computes `(x * y) + z` with a fused multiply-add instruction where the ISA provides one.
- Interfaces: exports/aliases `fmaf` and uses PowerPC floating-point instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `10` lines, `203` bytes read from the source file.
