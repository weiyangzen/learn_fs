<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-error.c -->
# sources/test-tools/stress-ng/stress-fp-error.c Research

Purpose: implements `fp-error`, a VERIFY_ALWAYS floating-point stressor that exercises math-domain, range, exception, errno, and rounding behavior.

Important APIs/types/functions: `stress_fp_error_info` exports the stressor or an unimplemented placeholder when functional FP error support is unavailable. `stress_fp_clear_error()` resets `errno` and clears all FP exceptions. `stress_double_same()` compares normal, NaN, and infinity results. `stress_fp_check()` validates result value, expected errno, and expected `fenv` exceptions on supported Linux/compiler combinations, with a value-only fallback elsewhere. `SET_VOLATILE` forces runtime computation for selected expressions.

Control flow: the stressor synchronizes workers, then repeatedly clears the FP status and evaluates `log(-1)`, `log(0)`, `log2(-1)`, `log2(0)`, `sqrt(-1)`, inexact division, overflow addition, underflow `exp(-1000000)`, overflow `exp(DBL_MAX)`, and `fegetround()`. Each enabled block is compile-time gated by `EDOM`, `ERANGE`, and `FE_*` macros. Failures set `rc = EXIT_FAILURE`, but the loop continues until the normal stress-ng stop condition.

State and persistence: only per-thread/process floating-point status flags and `errno` are mutated. There is no durable state. Volatile locals are used to prevent constant folding.

Dependencies and integration: depends on `<math.h>`, `<fenv.h>`, `<float.h>`, architecture/compiler feature macros, stress-ng sync/state/logging, and bogo counters. It is classified CPU/FP and requires verification.

Risks: FP exception and errno behavior varies across libcs, architectures, soft-float builds, and compilers. The code explicitly excludes uClibc, ARC64, some Linux architectures, musl/ICC/PCC cases, and soft-float paths from stricter checks. `M_PI` availability is assumed through the project configuration.

Test signals: failures are `pr_fail()` messages describing expression, result, errno, and exception mismatch. Useful coverage includes glibc Linux with hardware FP for strict checking and non-Linux or alternate libc builds to confirm fallback behavior or unimplemented registration.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-error.c -->
