<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_test.go -->
# sources/user-network-fs/rclone/vfs/read_test.go

## Purpose
Tests the direct read-only `ReadFileHandle` path used when VFS cache is not providing a RW cache handle.

## Important APIs, Types, and Functions
Helpers are `readHandleCreate` and `readString`. Tests are `TestReadFileHandleMethods`, `TestReadFileHandleSeek`, `TestReadFileHandleReadAt`, `TestReadFileHandleFlush`, and `TestReadFileHandleRelease`.

## Control Flow
The helper writes `dir/file1` with known contents, opens it read-only through `VFS.OpenFile`, asserts the returned handle type, then tests handle methods. Seek tests use start/current/end whence values and delayed read errors for off-end seeks. ReadAt tests exercise forward and backward seeks and reads crossing EOF.

## State and Persistence Behavior
The tests do not mutate remote contents. They validate in-memory offset movement, closed state, EOF behavior, `noSeek` behavior, and that `Flush` does not close the handle while `Release` closes after reading.

## Dependencies and Integration Points
Uses `fstest`, shared test VFS helpers, standard `io` and `os` flags, and testify assertions. It indirectly validates `VFS.OpenFile`, `File.openRead`, and `ReadFileHandle`.

## Risks and Edge Cases
The tests do not exercise checksum mismatch, low-level retry, sequential wait concurrency, chunk stream options, unknown-size objects, or source disappearance during close/hash. Those behaviors remain integration-risk areas.

## Test Signals
Strong signal for normal read handle API compatibility, offset handling, EOF semantics, close/flush/release behavior, and read-after-close error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_test.go -->
