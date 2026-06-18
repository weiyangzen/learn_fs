# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrt.S

- Role: `i387` square-root routine for `e_sqrt`.
- Key behavior: computes square root using the architecture FP sqrt instruction or FPSP wrapper.
- Interfaces: exports/aliases `__ieee754_sqrt` and uses x87 instructions with i386/x86_64 ABI helpers from `abi.h` where needed.
- Notes: selected by `libm/Makefile` as an architecture override for the generic C implementation.
- Read proof: `17` lines, `259` bytes read from the source file.
