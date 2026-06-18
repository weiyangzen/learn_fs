# sources/test-tools/ior/src/aiori-debug.h

## Purpose
Defines shared logging, warning, error, and MPI-check macros used by IOR AIORI backends and core code. It centralizes output formatting to `out_logfile`, verbosity-aware diagnostics, warning-as-error behavior, and MPI abort-on-failure handling.

## Important APIs, Types, And Functions
Declares external `FILE *out_logfile`, `int verbose`, and `int aiori_warning_as_errors`, plus `FailMessage`. Macros include `FAIL`, `WARN_RESET`, `WARNF`, `WARN`, `INFOF`, `INFO`, `ERRF`, `ERR`, `MPI_CHECKF`, and `MPI_CHECK`.

## Control Flow
Warning macros print on rank/verbosity conditions and flush logs. `WARNF` escalates to `ERRF` when `aiori_warning_as_errors` is set. `ERRF` and MPI check failures print file/line context, flush, and call `MPI_Abort(MPI_COMM_WORLD, -1)`. `WARN_RESET` copies a default member value into a target struct member and reports the reset on rank 0.

## State And Persistence Behavior
No persistent state is owned here; behavior depends on global log file, verbosity, MPI rank, and warning policy. The macros synchronously flush log output before aborting or returning to callers.

## Dependencies And Integration Points
Requires MPI and stdio. Included by `aiori.h` and many backend implementations, so it affects error behavior across POSIX, S3, AIO, and core IOR validation paths.

## Risks And Edge Cases
Macros evaluate some arguments in formatted contexts and can be unsafe with side effects. `ERRF` always aborts `MPI_COMM_WORLD`, which may be broader than a per-test communicator. `WARN_RESET` assumes integer formatting for the reset member. `FAIL` depends on `rank` and `ERROR_LOCATION` being visible where used. Format-string mismatches are easy because these are variadic macros.

## Test Signals
Compiler warnings with format checking, forced MPI failure paths, warning-as-error runs, and validation warnings from `ValidateTests` confirm these macros behave as expected.
