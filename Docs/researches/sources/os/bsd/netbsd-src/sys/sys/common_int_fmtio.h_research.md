# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_fmtio.h

## Scope

Defines C99 `<inttypes.h>` format-string macros for fixed-width integer printf/scanf operations.

## APIs And Behavior

- Requires compiler format macro support, checked via `__INTPTR_FMTd__`.
- Defines `PRI*` macros for signed decimal/integer, unsigned octal/decimal/hex/HEX, least-width, fast-width, max-width, and pointer-width integer formatting.
- Defines `SCN*` macros for scanf decimal/integer/octal/unsigned/hex/HEX variants across the same width families.

## Dependencies

- Relies on compiler-provided `__INT*_FMT*__`, `__UINT*_FMT*__`, least/fast/max/pointer format macros.

## Risks And Invariants

- These macros are string fragments; consumers concatenate them into format strings.
- Format macro correctness is ABI-sensitive for pointer and max-width integer types.
