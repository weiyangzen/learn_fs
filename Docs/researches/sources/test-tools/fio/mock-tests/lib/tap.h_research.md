# sources/test-tools/fio/mock-tests/lib/tap.h

Purpose: header-only minimal Test Anything Protocol emitter for mock C tests.

Important APIs/functions: `tap_init`, `tap_plan`, `tap_ok`, `tap_skip`, `tap_diag`, `tap_within_tolerance`, and `tap_done`. Static header variables track test count, failure count, and whether a plan was printed.

Control flow: tests initialize, optionally plan, emit ok/not-ok lines with formatted descriptions, emit diagnostics prefixed with `#`, and return `tap_done` as process exit status. If no plan was printed, `tap_done` prints one using the observed count.

State/persistence: per-translation-unit static counters in the header. No allocation or files.

Dependencies/integration: standard C stdio/stdarg/stdbool only. Used by `mock-tests/tests/test_latency_precision.c`.

Risks/test signals: because state is header-static, including it in multiple translation units would create independent TAP counters. `tap_skip` prints `ok N # SKIP` without a dash description. Tests should verify TAP output remains accepted by `prove`.
