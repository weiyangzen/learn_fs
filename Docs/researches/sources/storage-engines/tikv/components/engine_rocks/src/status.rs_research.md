<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/status.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/status.rs

## Purpose
`status.rs` provides minimal error conversion helpers between RocksDB-facing string errors and `engine_traits::Error`.

## Important APIs, Types, and Functions
`r2e(msg)` wraps a message in `engine_traits::Error::Engine(Status::with_error(Code::IoError, msg))`. `e2r(error)` formats an `engine_traits::Error` with debug formatting into a string for RocksDB callbacks.

## Control Flow
There is no branching beyond constructing the status or formatting the error.

## State and Persistence Behavior
The module has no state or persistence impact. It affects error classification visible to higher layers.

## Dependencies and Integration Points
Nearly every RocksDB adapter module uses `r2e` in `map_err`. Callback adapters use `e2r` when RocksDB expects a string error.

## Risks and Edge Cases
`r2e` currently maps all messages to `IoError`, losing more specific RocksDB status codes. That can make retry, corruption, invalid-argument, and not-found handling less precise. `e2r` is lossy and intended only for string-based callback boundaries.

## Test Signals
Tests should assert expected `Code::IoError` wrapping and ensure higher-level code does not depend on more specific status codes from these paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/status.rs -->
