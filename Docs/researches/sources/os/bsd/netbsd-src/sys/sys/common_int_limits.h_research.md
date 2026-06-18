# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_limits.h

Defines the C99 `<stdint.h>`/`<inttypes.h>` integer limit macros using compiler-provided builtin macros such as `__INT8_MAX__`, `__UINTPTR_MAX__`, and `__SIZE_MAX__`.

Key content:
- Exact-width limits: `INT8_MIN/MAX`, `UINT8_MAX`, through 64-bit.
- Least/fast integer limits: `INT_LEAST*`, `UINT_FAST*`.
- Pointer and maximum-width limits: `INTPTR_*`, `UINTPTR_MAX`, `INTMAX_*`.
- Other type limits: `PTRDIFF_*`, `SIG_ATOMIC_*`, `SIZE_MAX`.

Important behavior:
- Fails preprocessing if the compiler lacks `__SIG_ATOMIC_MAX__`.
- Signed minima are expressed as `(-MAX-1)` to avoid direct unrepresentable literal constants.
- This is ABI-sensitive infrastructure for system headers, not runtime code.
