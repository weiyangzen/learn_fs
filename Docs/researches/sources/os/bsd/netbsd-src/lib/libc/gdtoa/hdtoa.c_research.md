# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hdtoa.c

Purpose: Converts `double` and `long double` values to hexadecimal digit strings.

Core behavior:
- `roundup()` increments a hexadecimal digit buffer and reports exponent carry.
- `dorounding()` applies `FLT_ROUNDS` to a generated hex digit buffer.
- `hdtoa()` handles double sign, zero, normal, subnormal, infinity, and NaN values.
- `hdtoa()` emits nibble-aligned hexadecimal significand digits and binary exponent `decpt`.
- `hldtoa()` provides the same behavior for `long double` when it has greater precision than double; otherwise it delegates to `hdtoa`.
- Uses `INT_MAX` as the special exponent for infinity/NaN instead of dtoa's `9999`.

Dependencies:
- Uses `<machine/ieee.h>` or VAX floating definitions, `<float.h>`, `<math.h>`, and `gdtoaimp.h`.
- Uses `rv_alloc` and `nrv_alloc`.
