<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_stream.c -->
# sources/storage-engines/wiredtiger/src/packing/pack_stream.c

## Purpose
Implements one-field-at-a-time streaming pack/unpack APIs for applications and extensions.

## Important APIs, Types, and Functions
`WT_PACK_STREAM` stores parser state and buffer pointers. Public methods include `wiredtiger_pack_start`, `wiredtiger_unpack_start`, close, item/int/str/uint packers, and matching unpackers. Extension wrappers `__wt_ext_pack_*` and `__wt_ext_unpack_*` delegate to public methods.

## Control Flow
Start allocates a stream, initializes format parsing, and sets start/current/end pointers. Each pack/unpack method checks remaining space, advances to the next format field, verifies the requested type class, and calls `__pack_write` or `__unpack_read`. Close optionally reports bytes used and frees the stream.

## State and Persistence Behavior
Stream state is in memory and progresses monotonically through the format and buffer. No persistent state is written.

## Dependencies and Integration Points
Used by public WiredTiger APIs and extension API tables. Depends on lower-level packing parser and value encoders.

## Risks and Edge Cases
The zero-length check prevents lower layers from treating zero as unchecked. Type mismatches return illegal-value errors. Callers must not use a closed stream or mutate the backing buffer unexpectedly.

## Test Signals
Streaming round trips, type mismatch errors, buffer boundary/ENOMEM cases, bytes-used reporting, and extension default-session paths should be covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_stream.c -->
