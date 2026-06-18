# sources/test-tools/crashmonkey/code/tests/sync_file_range_inconsistency.cpp

Purpose: generated/handwritten CrashMonkey workload for a suspected `sync_file_range` inconsistency. It creates `A/foo`, preallocates/zeroes 8 KiB, syncs, checkpoints, writes 4 KiB at offset 4096, calls `sync_file_range` with wait/write flags, then checkpoints again.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmSync`, `CmSyncFileRange`, `CmCheckpoint`, `CmClose`, `fallocate`, and `SYNC_FILE_RANGE_WAIT_BEFORE|WRITE|WAIT_AFTER`. It includes a commented `CmFdatasync` alternative, documenting that the range sync is the behavior under test.

Control flow: `setup` initializes paths. `run` creates directory `A`, opens `A/foo`, zero-ranges 8 KiB, global-syncs, records checkpoint 1, optionally exits, writes 4 KiB into the second page, calls `CmSyncFileRange` for that page, records checkpoint 2, closes, and returns `1` if the caller requested the second checkpoint. `check_test` is a no-op.

State/persistence behavior: the two checkpoint boundaries separate initial preallocation from later range-flushed data. The wrapper records `kSyncFileRangeMod` with offset, length, path, and post-stat metadata but no data payload.

Dependencies/integration: relies on Linux `sync_file_range`, CrashMonkey checkpoint IPC, and external diffing. Risks/test signals: no local oracle, direct fallocate bypasses wrapper recording, and `sync_file_range` durability semantics are intentionally subtle and filesystem/kernel dependent.
