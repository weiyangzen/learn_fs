# sources/object-store/daos/src/vos/pmdk_log.c

## Purpose
Bridges PMDK/libpmemobj logging into DAOS logging when built with persistent-memory support. It registers a PMDK log callback that maps PMDK severity levels to DAOS log levels and formats messages with PMDK source location.

## Important APIs, Types, And Functions
`pmdk_log_attach` is the exported entry point. Under `DAOS_PMEM_BUILD`, `pmdk_log_function` is registered with `pmemobj_log_set_function`. The severity table maps `PMEMOBJ_LOG_LEVEL_*` values to DAOS `DLOG_*` levels and saved masks. `PMDK_LOG_NOCHECK` adapts DAOS logging internals to use callback-provided file, line, and function data.

## Control Flow
At attach time, DAOS asks PMDK to use `pmdk_log_function`. For each PMDK message, the callback normalizes leading `../` and `src/../src` path patterns, prefixes the filename with `pmdk/`, then emits through DAOS logging with the mapped severity and saved mask.

## State And Persistence
No persistent state. Runtime state is the static mapping table and PMDK's registered callback pointer.

## Dependencies And Integration
Compiled only with `DAOS_PMEM_BUILD`; depends on `daos/debug.h`, `daos/common.h`, `libpmemobj/log.h`, and `libpmemobj.h`. The path prefix is intentionally used by DAOS pipeline/NLT log filtering.

## Risks
The non-PMEM stub contains only `;` in an `int` function, which relies on compiler behavior and should return a value for strict builds. The callback indexes the severity table by PMDK enum value; new/out-of-range PMDK levels would be unsafe unless PMDK guarantees the enum range. It uses DAOS internal logging macros, so logging API changes could break it.

## Test Signals
Build tests should cover both PMEM and non-PMEM configurations. Runtime tests can inject PMDK messages and verify DAOS severity, filename normalization, and `pmdk/` prefix.
