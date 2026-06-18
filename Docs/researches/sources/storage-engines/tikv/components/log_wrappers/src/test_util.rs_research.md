# sources/storage-engines/tikv/components/log_wrappers/src/test_util.rs

## Purpose
This file provides a synchronized in-memory logging buffer for tests that need deterministic `slog` output.

## Important APIs, Types, and Functions
- `SyncLoggerBuffer` wraps `Arc<Mutex<Vec<u8>>>`.
- `new` creates an empty buffer.
- `build_logger` builds a compact `slog::Logger` with a constant `TIME` timestamp.
- `as_string` clones and decodes the buffer as UTF-8.
- `clear` empties buffered bytes.
- The `io::Write` impl appends to the shared byte vector and flushes the vector writer.

## Control Flow
Tests create a buffer, build a logger from a clone, emit logs, and inspect `as_string`. Writes lock the buffer for each append.

## State and Persistence Behavior
State is process-local test memory protected by a mutex. No persistence.

## Dependencies and Integration Points
Used by `log_wrappers` tests. It depends on `slog-term` compact formatting and the `o!` macro imported at crate root.

## Risks
`as_string` panics if log output is not UTF-8, which is fine for current text logs. Mutex poisoning also panics through `unwrap`. The deterministic timestamp means tests should not use this utility to validate real time formatting.

## Test Signals
Its behavior is exercised by `log_wrappers` tests that compare exact log lines.
