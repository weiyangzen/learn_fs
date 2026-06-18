# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/math.c

Checked math wrappers for `hoc` builtins.

- Wraps `log`, `log10`, `sqrt`, `exp`, `asin`, `acos`, `sinh`, `cosh`, and `pow`.
- `integer()` validates 32-bit signed range before casting to `long`.
- `errcheck()` maps NaN to “argument out of domain” and infinity to “result out of range” through `execerror()`.

Dependencies are Plan 9 math predicates `isNaN`/`isInf`, libc math functions, and `hoc.h`.

Notable concern: only selected math functions are range-checked through wrappers; direct builtins like `sin`, `cos`, `tan`, `atan`, `tanh`, and `fabs` are installed directly.
