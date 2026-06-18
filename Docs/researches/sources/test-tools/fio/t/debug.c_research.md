# sources/test-tools/fio/t/debug.c

## Purpose
Provides a minimal debug/logging shim for small fio test tools that link against fio internals but do not need the full fio debug subsystem.

## Important APIs, Types, and Functions
Defines global symbols `FILE *f_err`, `void *fio_ts`, and `unsigned long fio_debug` expected by linked fio objects. Exports `__dprint()` as a no-op variadic debug printer and `debug_init()` to point `f_err` at `stderr`.

## Control Flow
There is no complex flow: callers invoke `debug_init()` during startup, after which fio logging code that writes via `f_err` has a valid stream.

## State and Persistence Behavior
Only process-global debug state is provided. No persistent files are written.

## Dependencies and Integration Points
Integrated by test programs such as `dedupe.c` via `debug.h`, satisfying linker references from shared fio code paths without pulling the full application.

## Risks
All debug output is silently discarded through `__dprint()`, so problems in linked fio internals can be harder to diagnose. The global `fio_ts` is only a stub and must not be relied on for real fio thread state.

## Test Signals
The main signal is successful link/startup of utilities that include fio internals and call `debug_init()`.
