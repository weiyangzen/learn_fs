# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/log2.h

This header provides Linux-style integer base-2 helpers.

Key content:
- Declaration for `____ilog2_NaN`.
- Inline `__ilog2_u32` and `__ilog2_u64`, unless architecture overrides are configured.
- `is_power_of_2`.
- Runtime `__roundup_pow_of_two` and `__rounddown_pow_of_two`.
- Macros `ilog2`, `roundup_pow_of_two`, `rounddown_pow_of_two`, and `order_base_2`.

Role:
- Used by allocation, extent, journal, and bitmap code that needs block/order sizing.
- Relies on `fls`, `fls64`, and `fls_long` from `bitops.h`.

Notable behavior:
- The constant `rounddown_pow_of_two(1)` branch returns `0`, matching the file’s current macro text even though callers may expect `1` from a mathematical round-down helper.
