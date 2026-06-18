# sources/user-network-fs/rclone/lib/readers/readfill_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill_test.go -->
## sources/user-network-fs/rclone/lib/readers/readfill_test.go

Purpose: tests `ReadFill` for EOF-before-data, partial fill with EOF, and full fill without error.

Important APIs and control flow: a custom `byteReader` emits decreasing byte values one byte per read until reaching EOF. `TestReadFill` verifies buffer contents and returned `(n, err)` for zero, three, and eight available bytes against a five-byte target buffer.

State, dependencies, and integration: dependencies are `io`, `testing`, and testify. The test intentionally leaves unread portions of the buffer unchanged for partial reads.

Risks and test signals: verifies core semantics but not the pathological `(0, nil)` reader case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill_test.go -->
