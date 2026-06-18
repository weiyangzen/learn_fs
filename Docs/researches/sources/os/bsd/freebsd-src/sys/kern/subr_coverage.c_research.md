# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_coverage.c

## Purpose
Provides compiler sanitizer coverage entry points for kernel coverage/fuzzing instrumentation and dynamic registration of coverage callbacks.

## Main Elements
- Callback registration:
  - `cov_register_pc()` / `cov_unregister_pc()` install or clear the PC tracing callback.
  - `cov_register_cmp()` / `cov_unregister_cmp()` install or clear the comparison tracing callback.
- Sanitizer coverage hooks:
  - `__sanitizer_cov_trace_pc()` records the caller return address through `cov_trace_pc`.
  - `__sanitizer_cov_trace_cmp1/2/4/8()` records non-constant comparisons with size tags.
  - `__sanitizer_cov_trace_const_cmp1/2/4/8()` records constant comparisons with `COV_CMP_CONST`.
  - `__sanitizer_cov_trace_switch()` decodes sanitizer switch metadata and emits comparison records for each case.
- Callback pointers are read and written with atomic pointer operations.

## Dependencies And Integration
Uses `<sys/coverage.h>` callback types and comparison flag macros. Built to satisfy compiler-inserted sanitizer coverage calls, optionally defining `SAN_RUNTIME` when interceptors are needed.

## Risk Notes
These hooks may execute at very high frequency, so the fast path is minimal: atomic callback load and NULL check. Callback implementations must tolerate arbitrary instrumented call sites. `__sanitizer_cov_trace_switch()` trusts the compiler-provided case array layout and rejects unsupported operand sizes.
