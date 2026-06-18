# File Research: sources/os/bsd/dragonflybsd/sys/sys/bitops.h

Read completely: 165 lines.

This header provides bit-mask and bit-field helper macros.

Key contents:
- `__BIT`/`__BIT64` for single-bit masks.
- `__BITS`/`__BITS64` for inclusive bit ranges.
- `__LOWEST_SET_BIT`, `__SHIFTOUT`, `__SHIFTIN`, and `__SHIFTOUT_MASK` for register bitfields.
- `ilog2()` using compile-time expansion for constants and `fls`/`flsl` for runtime values.

Security/reliability notes:
- Macro inputs are not generally validated; invalid shift counts or zero masks can produce undefined or nonsensical results.
- `__BIT(32)` and `__BIT64(64)` deliberately return zero to support range macro edge cases.
