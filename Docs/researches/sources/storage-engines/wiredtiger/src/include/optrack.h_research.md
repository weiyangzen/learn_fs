# sources/storage-engines/wiredtiger/src/include/optrack.h

## Purpose
Defines lightweight per-session operation tracking records and macros that log function entry/exit timestamps to a session buffer for later decoding.

## Important APIs, Types, And Functions
- `WT_OPTRACK_MAXRECS`, `WT_OPTRACK_BUFSIZE`, and `WT_OPTRACK_VERSION` define buffer and file-format sizing/version.
- `struct __wt_optrack_header` records version, internal-session flag, timestamp ratio, padding, and epoch seconds.
- `struct __wt_optrack_record` is a 16-byte event containing timestamp, function id, operation type, and explicit padding.
- `WT_TRACK_OP`, `WT_TRACK_OP_DECL`, `WT_TRACK_OP_INIT`, and `WT_TRACK_OP_END` instrument functions.

## Control Flow
Instrumented functions declare a static function id. On entry, `WT_TRACK_OP_INIT` checks the connection optrack flag and excludes the default session. It lazily records the function name/id mapping, then appends a start record. `WT_TRACK_OP_END` appends a stop record. `WT_TRACK_OP` writes into the circular buffer and flushes when the pointer reaches `WT_OPTRACK_MAXRECS`.

## State And Persistence Behavior
Per-session buffers and file handles are runtime state, but flushed optrack logs are persistent diagnostic artifacts with a versioned binary layout. Function ids are process-local mappings recorded separately for decoding.

## Dependencies And Integration Points
Depends on session optrack fields, connection flags, clocks, function-id recording, and buffer flush routines. It integrates with performance diagnostics and requires instrumentation at function boundaries.

## Risks
The macros intentionally avoid synchronization on the session buffer and can lose records if a session is used by multiple threads. Static function ids are per-process and need mapping records to decode. The default session is excluded because it can be multi-threaded and used during error paths.

## Test Signals
Tests should enable operation tracking, instrument simple functions, verify start/stop records and flush boundaries, decode function mappings, confirm default-session exclusion, and stress concurrent misuse to ensure failures are bounded to lost diagnostics rather than memory corruption.
