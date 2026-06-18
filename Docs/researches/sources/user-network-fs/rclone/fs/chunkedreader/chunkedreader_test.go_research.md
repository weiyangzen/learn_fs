# sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader_test.go

Purpose: contains shared tests and helpers for sequential and parallel chunked readers.

Important APIs/functions: `TestMain` initializes fstest. `TestChunkedReader` validates `New` chooses `sequential` or `parallel`. `testRead` returns a reusable subtest that performs many `RangeSeek` plus `Read` checks over content. `testErrorAfterClose` validates closed readers reject `Close`, `Read`, `Seek`, and `RangeSeek`. `makeContent` creates deterministic random bytes.

Control flow: `testRead` iterates initial chunk sizes, max chunk sizes, offsets, and range lengths, calling `RangeSeek` then reading a fixed 32-byte buffer and comparing exact content. Offsets beyond content length must error. The helper is invoked by sequential and parallel-specific tests with different stream counts.

State and persistence behavior: no persistence. It documents that `RangeSeek` should defer opening until read and should preserve byte-exact offsets across chunk boundaries.

Dependencies and integration points: uses `mockobject` seek modes, `fstest`, `testify`, and shared error values from the package. It validates both implementations through the public constructor and interface.

Risks: tests use small content and a fixed read buffer, so very large stream behavior is handled in `parallel_test.go`. Error-after-close asserts errors generically rather than exact error values.

Test signals: high signal for public behavior consistency across implementations and source seek modes.
