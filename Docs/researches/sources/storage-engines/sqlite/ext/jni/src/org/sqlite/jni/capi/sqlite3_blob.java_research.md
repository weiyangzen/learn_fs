# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_blob.java

## Purpose
`sqlite3_blob` wraps C `sqlite3_blob*` incremental BLOB handles.

## Important APIs, Types, and Functions
The class extends `NativePointerHolder<sqlite3_blob>` and implements `AutoCloseable`; `close()` delegates to `CApi.sqlite3_blob_close(this)`.

## Control Flow
Instances are opened through `sqlite3_blob_open()` overloads, used with read/write/reopen APIs, and closed explicitly or by try-with-resources.

## State and Persistence Behavior
The wrapper is a typed pointer carrier. Closing invalidates the native pointer. Reopen keeps the same handle but changes target row.

## Dependencies and Integration Points
It integrates with `CApi.sqlite3_blob_open`, `sqlite3_blob_read`, `sqlite3_blob_write`, `sqlite3_blob_reopen`, `sqlite3_blob_bytes`, and ByteBuffer-specific overloads when JNI NIO support is available.

## Risks
Offset/length validation is important for byte arrays and direct buffers. Open writable blob handles can hold locks; handles must be closed on all paths.

## Test Signals
`Tester1.testBlobOpen()` validates open/write/close, double-close error behavior, reopen, byte-array read, NIO read/write bounds checks, returned direct-buffer limits, and final database contents.
