# sources/user-network-fs/rclone/fs/chunkedreader/sequential_test.go

Purpose: runs the shared chunked reader tests against sequential mode.

Important APIs/functions: `TestSequential` creates deterministic 1024-byte content and runs `testRead` over all `mockobject.SeekModes` with streams set to zero. `TestSequentialErrorAfterClose` reuses shared close-error checks.

Control flow: the tests go through the public `New` constructor, which selects `sequential` because stream count is zero. The blank local backend import ensures backend registration for fstest context.

State and persistence behavior: no persistence. It validates sequential state transitions through public reads, range seeks, and closing.

Dependencies and integration points: depends on `mockobject`, shared test helpers, and local backend registration.

Risks: this file is intentionally thin; detailed coverage lives in `chunkedreader_test.go`.

Test signals: confirms the shared behavior matrix applies to sequential mode.
