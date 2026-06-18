# File Research: sources/os/bsd/freebsd-src/sys/sys/csan.h

## Purpose
Declares conditional kernel concurrency sanitizer CPU initialization.

## Main Elements
- If `KCSAN` is enabled, declares `kcsan_cpu_init(u_int)`.
- Otherwise maps `kcsan_cpu_init(ci)` to a no-op.

## Dependencies And Integration
Includes `sys/types.h`. Used by CPU bring-up code without needing preprocessor conditionals at call sites.

## Risk Notes
The no-op fallback means callers cannot infer sanitizer availability from successful compilation.
