# sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurability.cpp

Purpose: Defines an `AsyncFileWorkload` that repeatedly writes and verifies unbuffered file pages to catch non-durable or torn disk writes.

Important APIs/types/functions: `DiskDurabilityWorkload`, nested `FileBlock`, `FileBlock::test_impl`, `IAsyncFileSystem::open`, `AsyncFileHandle`, `AsyncFileBuffer`, `FlowLock`, `worker`, `syncLoop`, and `_PAGE_SIZE`.

Control flow: Setup opens/creates the configured file with read-write, unbuffered, and uncached flags. Start constructs one `FileBlock` per page, launches a randomized sync loop plus writer actors, and runs them for `testDuration`. Each worker chooses skewed random blocks, serializes access through the block lock, reads previous contents when expected, verifies all int64 words equal the last value, writes a new value across the block, and updates `lastData`.

State and persistence behavior: Persistent state is the test file. Runtime state is per-page `lastData` and locks; it is not persisted across workload restarts. Syncs happen at random intervals up to `syncInterval`.

Dependencies/integration: It relies on Flow async file APIs, `AsyncFileWorkload` options/path handling, deterministic randomness, and OS support for unbuffered/uncached file modes.

Risks: The code increments `newData` from zero rather than from `lastData`, so after the first write later writes use value 1 unless `lastData` is zero; the verification still catches durability mismatch for the previous value. Lock release occurs after successful write, so exceptions can leave a block lock held.

Test signals: `WriteWasNotDurable` with filename, offset, expected/found values is the primary failure; otherwise the workload exports no metrics.
