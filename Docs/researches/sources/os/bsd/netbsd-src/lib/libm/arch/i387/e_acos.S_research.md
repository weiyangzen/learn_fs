# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_acos.S

i387 `__ieee754_acos` implementation. It computes `acos(x)` as `atan(sqrt(1 - x*x) / x)` using x87 stack operations, `fsqrt`, `fabs`, and `fpatan`.
