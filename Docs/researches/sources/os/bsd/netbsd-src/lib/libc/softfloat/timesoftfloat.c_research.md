# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/timesoftfloat.c

Read completely: 2641 lines.

This file is the SoftFloat release 2a timing driver. It defines fixed integer, float32, float64, and conditionally floatx80/float128 input vectors, then measures SoftFloat conversion, arithmetic, remainder, square-root, rounding, and comparison functions by repeatedly calling them for at least one clock-second warmup and reporting kops/s.

Key behavior: command-line parsing accepts one function name or `all`, `all1`, `all2`, plus rounding precision, rounding mode, and tininess options. The `functions[]` metadata table records each operation's arity and whether it should be timed across rounding precision, rounding mode, tininess mode, or reduced-precision tininess variants. `timeFunctionVariety` sets global SoftFloat state such as `float_rounding_mode`, `float_detect_tininess`, and, for extended precision builds, `floatx80_rounding_precision`, then dispatches to the matching timing wrapper.

Important interactions: this is a benchmark/test utility for the SoftFloat implementation included in libc, not normal libc runtime code. It depends on `milieu.h`, `softfloat.h`, optional `FLOATX80`/`FLOAT128` build configuration, and every exported SoftFloat arithmetic primitive.

Security/reliability notes: benchmark accuracy depends on `clock()` resolution, compiler optimization behavior, and the fixed input distributions. The code uses old-style implicit `int main`, global mutable SoftFloat mode variables, and repeated boilerplate wrappers, so it is useful as legacy test infrastructure but not a modern harness.
