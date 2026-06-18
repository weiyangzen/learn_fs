# sources/storage-engines/wiredtiger/src/include/error.h

## Purpose
`error.h` centralizes WiredTiger error propagation, diagnostic assertions, panic handling, branch prediction hints, and optional error logging hooks. It provides the macros that make the codebase's `ret`/`err:` cleanup style consistent.

## Important APIs, Types, and Functions
Logging/reporting wrappers include `__wt_err`, `__wt_errx`, `__wt_panic`, and `__wt_set_return`, which pass function and line metadata. `WT_ERR*` macros set `ret` and jump to `err`; `WT_RET*` macros return immediately; `WT_TRET*` macros preserve cleanup errors only when they should override an existing return. `WT_ERROR_LOG_ADD` and helpers integrate optional error-log recording.

Diagnostic macros include `WT_DIAGNOSTIC_YIELD`, `WT_ASSERT`, `WT_ASSERT_OPTIONAL`, `WT_ASSERT_ALWAYS`, `WT_ERR_ASSERT`, `WT_RET_ASSERT`, `WT_RET_PANIC_ASSERT`, and `WT_PREFETCH_ASSERT`. `TRIGGER_ABORT` either aborts or records assertion hits for unit-test assertion builds. `WT_LIKELY`/`WT_UNLIKELY` wrap compiler branch prediction.

## Control Flow
Most functions declare `WT_DECL_RET`, use `WT_ERR(...)` for fallible operations, and perform cleanup at `err:` with `WT_TRET(...)` for secondary failures. Immediate-return functions use `WT_RET(...)`. Assertion macros either compile away, abort, return normal errors, or return panic depending on build mode and runtime diagnostic categories.

## State and Persistence Behavior
The macros update session last-error state, optional error logs, statistics in some specialized paths, and connection panic state through panic functions. They do not persist data, but they control whether operations continue, return recoverable errors, or abort the process.

## Dependencies and Integration Points
This file is included broadly across WiredTiger. It depends on session/connection error functions, optional `HAVE_ERROR_LOG` and `HAVE_UNITTEST_ASSERTS` builds, diagnostic flags from `connection.h`, verbose categories, and statistics macros for prefetch assertions.

## Risks and Edge Cases
Macro semantics depend on local names such as `ret`, `err`, and `session`, so misuse can compile incorrectly or alter control flow unexpectedly. `WT_TRET` precedence intentionally lets `WT_PANIC` and selected cleanup errors override prior returns; changing it can hide data-corruption signals. Assertions vary significantly by build and runtime diagnostic settings, so tests must cover both aborting and non-aborting modes.

## Test Signals
Error-path unit tests, fault-injection tests, assertion unit tests with `HAVE_UNITTEST_ASSERTS`, panic/corruption tests, and cleanup paths with multiple failures validate this header. Static analysis can catch macros used without required local variables.
