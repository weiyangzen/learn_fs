# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/math.c

Provides checked math wrappers for `hoc` builtins.

Key points:
- Wraps `log`, `log10`, `sqrt`, `exp`, `asin`, `acos`, `sinh`, `cosh`, and `pow`.
- `integer` rejects values outside signed 32-bit integer range before casting to `long`.
- `errcheck` raises `execerror` on NaN results as domain errors and infinity results as range errors.

Dependencies and interactions:
- Uses Plan 9 `isNaN` and `isInf`.
- Reports runtime errors via `execerror` from `hoc.y`.
- Registered by `init.c`.

Research relevance:
- This file turns raw libc math behavior into recoverable interpreter errors.
