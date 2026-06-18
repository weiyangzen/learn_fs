# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_sqrt.S

- Role: `mc68881` square-root routine for `e_sqrt`.
- Key behavior: computes square root using the architecture FP sqrt instruction or FPSP wrapper.
- Interfaces: exports/aliases `__ieee754_sqrt` and uses Motorola 68881 FP instructions.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `56` lines, `2193` bytes read from the source file.
