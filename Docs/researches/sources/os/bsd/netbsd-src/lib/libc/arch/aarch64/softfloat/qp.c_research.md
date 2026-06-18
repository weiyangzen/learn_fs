# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/qp.c

AArch64 quad-precision helper wrapper file.

Key behavior:
- Includes SoftFloat environment and API headers.
- Defines unions to reinterpret `float`, `double`, and `long double` as SoftFloat `float32`, `float64`, and `float128`.
- Exports `long double __negtf2(long double)`.
- Implements `__negtf2` by creating a zero `long double`, reinterpreting inputs as `float128`, computing `float128_div(zero, a)`, and returning the resulting long double.

Dependencies:
- SoftFloat `float128_div`.
- AArch64 long double / float128 ABI distinction described in comments.

Notes:
- Comment says most quad helpers now come from compiler_rt; this file remains for a missing function.
