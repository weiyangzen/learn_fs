# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sqrtf.S

- Role: `m68060` square-root routine for `e_sqrtf`.
- Key behavior: computes square root using the architecture FP sqrt instruction or FPSP wrapper.
- Interfaces: exports/aliases `__ieee754_sqrtf` and uses m68060 assembly wrappers around FPSP/FPLSP offset entry points.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `22` lines, `482` bytes read from the source file.
