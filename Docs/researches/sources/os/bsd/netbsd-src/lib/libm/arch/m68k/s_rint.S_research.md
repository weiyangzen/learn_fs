# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_rint.S

- Role: `m68k` rounding routine for `s_rint`.
- Key behavior: temporarily uses the target rounding mode/control word or native integer-round operation, then restores FP state.
- Interfaces: exports/aliases `rint` and uses m68k/m68881-style FP instructions and control-register manipulation.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `52` lines, `2190` bytes read from the source file.
