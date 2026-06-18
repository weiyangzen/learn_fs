# sources/storage-engines/foundationdb/flow/include/flow/DebugTrace.h

## Purpose
`DebugTrace.h` provides compile-time-disabled trace macros for narrowly scoped debug channels without removing call sites.

## Important APIs, Types, And Functions
It defines `DebugTraceEvent(enable, ...)`, constants `debugLogTraces` and `debugRelocationTraces`, and convenience macros `DebugLogTraceEvent(...)` and `DebugRelocationTraceEvent(...)`.

## Control Flow
The macro expands to `enable && TraceEvent(...)`, so disabled constexpr flags short-circuit event construction. Enabling a flag at compile time activates the associated trace stream.

## State And Persistence Behavior
The header owns no runtime state. Any persisted output is produced by `TraceEvent` only when a debug flag is enabled.

## Dependencies And Integration Points
It relies on `TraceEvent` being visible at call sites. It integrates with Flow tracing but intentionally avoids including heavy trace headers itself.

## Risks And Edge Cases
Because the macro uses `&&`, argument side effects should be avoided. Debug constants are global constexprs, so enabling them affects every included call site and may add high trace volume.

## Test Signals
Signals are compile checks in files using the macros, plus a targeted debug build that flips a flag and verifies trace events compile and are emitted.
