# sources/user-network-fs/rclone/vfs/write_test.go

## Purpose
Tests `WriteFileHandle` behavior for streaming writes, close/flush/release, truncation rules, readonly remotes, modtime, and readback.

## APIs, Flow, And State
`writeHandleCreate` opens `file1` for write and asserts a `*WriteFileHandle`. Tests check `String`, `Node`, offset, stat, rejected read methods, no-op sync, truncate-at-offset, double close, open-existing behavior, O_TRUNC behavior, sequential `WriteAt`, closed-handle errors, unwritten `Flush`, `Release`, open-writer modtime preservation, and `ReadAt` after closing zero or nonzero files. The readonly test changes local remote directory permissions and verifies close returns upload errors and failed placeholders are removed.

## Dependencies And Integration
Uses `newTestVFS`, local `fstest` remotes, `fs.ErrorCantUploadEmptyFiles`, random data, and shared listing helpers. It is the focused unit/regression suite for `write.go`.

## Risks And Test Signals
Some tests skip Windows or non-local remotes, and empty-file behavior depends on backend support. Coverage is strong for sequential streaming semantics and close-time error propagation but does not test high concurrency.
