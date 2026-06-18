# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_limits.h

This header implements integer limit macros for illumos fixed-width and related standard types.

Key definitions:
- Maximums: `INT8_MAX`, `INT16_MAX`, `INT32_MAX`, optionally `INT64_MAX`; unsigned equivalents; `INTMAX_MAX`, `UINTMAX_MAX`.
- Least and fast integer max macros.
- Pointer integer max macros: `INTPTR_MAX`, `UINTPTR_MAX`.
- `PTRDIFF_MAX`, `SIZE_MAX`, `SIG_ATOMIC_MAX`, `WCHAR_MAX`, `WINT_MAX`.
- Minimums are exposed under extensions/non-XOPEN or XPG6 conditions:
  - `INT*_MIN`, `INTMAX_MIN`, least/fast min macros, `INTPTR_MIN`, `PTRDIFF_MIN`, `SIG_ATOMIC_MIN`, `WCHAR_MIN`, `WINT_MIN`.

Data model behavior:
- Uses `L` constants on `_LP64`.
- Uses `LL` constants when `_LONGLONG_TYPE` exists on ILP32.
- `SIZE_MAX` follows LP64/ILP32 `unsigned long` width.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Foundational ABI/standards header used across kernel and user code.
