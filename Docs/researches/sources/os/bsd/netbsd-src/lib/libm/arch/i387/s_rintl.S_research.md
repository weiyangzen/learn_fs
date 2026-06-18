# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rintl.S

- Role: `i387` rounding routine for `s_rintl`.
- Key behavior: temporarily uses the target rounding mode/control word or native integer-round operation, then restores FP state.
- Interfaces: exports/aliases `rintl` and uses x87 instructions with i386/x86_64 ABI helpers from `abi.h` where needed.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `39` lines, `1638` bytes read from the source file.
