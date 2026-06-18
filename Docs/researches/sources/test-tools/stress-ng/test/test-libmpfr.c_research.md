# sources/test-tools/stress-ng/test/test-libmpfr.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_MPFR` and link flags `-lmpfr -lgmp` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `gmp.h`, `mpfr.h`. Defined functions: `main`. Referenced calls/builtins: `mpfr_init2`, `mpfr_const_pi`, `mpfr_set_d`, `mpfr_set_ui`, `mpfr_mul`, `mpfr_mul_ui`, `mpfr_add_ui`, `mpfr_div`, `mpfr_div_ui`, `mpfr_ui_div`, `mpfr_add`, `mpfr_prec_round`, `mpfr_cmp`, `mpfr_set`. Important scalar/library types: `mpfr_t`, `mpfr_prec_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mpfr_init2`, `mpfr_const_pi`, `mpfr_set_d`, `mpfr_set_ui`, `mpfr_mul`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `gmp.h`, `mpfr.h`; linker availability for `-lmpfr -lgmp`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_MPFR`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 58 lines.

- Probe category: external library/header link probe.

- Includes: gmp.h, mpfr.h.

- Calls/builtins detected: mpfr_init2, mpfr_const_pi, mpfr_set_d, mpfr_set_ui, mpfr_mul, mpfr_mul_ui, mpfr_add_ui, mpfr_div, mpfr_div_ui, mpfr_ui_div, mpfr_add, mpfr_prec_round, mpfr_cmp, mpfr_set, mpfr_exp, mpfr_sin, mpfr_cos, mpfr_log, mpfr_clear, mpfr_free_cache.

- Structs/types detected: mpfr_t, mpfr_prec_t.
