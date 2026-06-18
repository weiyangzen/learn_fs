# sources/storage-engines/wiredtiger/src/optrack/optrack.c

## Purpose
Implements lightweight operation tracking output: mapping function names to process-unique IDs and flushing per-session binary operation records to session-specific files.

## Important APIs, Types, and Functions
`__wt_optrack_record_funcid` assigns and records a 16-bit function ID. `__optrack_open_file` creates the current session's optrack file and writes `WT_OPTRACK_HEADER`. `__wt_optrack_flush_buffer` opens the file on demand and writes buffered `WT_OPTRACK_RECORD` entries.

## Control Flow
Function ID recording allocates scratch space, locks `conn->optrack.map_spinlock`, assigns the static process-lifetime ID if the caller's ID is zero, appends `id name` to the map file, and panics on initialization failures. Flush opens the session file if needed, then directly calls the file handle's `fh_write` at `session->optrack_offset` and advances the offset on success.

## State and Persistence Behavior
Persistent artifacts are the optrack map file and per-session optrack files named by path, process ID, and session ID. Session state includes `optrack_fh`, `optrack_offset`, buffer pointer, and record buffer. The header persists version, internal-session flag, timestamp-counter conversion ratio, and epoch seconds.

## Dependencies and Integration Points
It depends on filename construction, file handle open/write/size, scratch buffers, connection optrack configuration, process timing ratio, and the session instrumentation macros that fill `optrack_buf`.

## Risks and Edge Cases
The function ID counter is static and 16-bit, so extremely many instrumented functions would wrap. The hot flush path deliberately bypasses standard write wrappers for overhead, so it also bypasses some accounting and throttling. Failed file opening just drops flush output. Map-file failures panic because IDs would become undecodable.

## Test Signals
Enable optrack and verify map-file entries, per-session headers, internal-session flags, monotonically advancing offsets, and decodeability of records. Error injection around map file writes should panic.
