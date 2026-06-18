# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rint.S

- Role: `i387` rounding routine for `s_rint`.
- Key behavior: temporarily uses the target rounding mode/control word or native integer-round operation, then restores FP state.
- Interfaces: exports/aliases `rint` and uses x87 instructions with i386/x86_64 ABI helpers from `abi.h` where needed.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `17` lines, `277` bytes read from the source file.
