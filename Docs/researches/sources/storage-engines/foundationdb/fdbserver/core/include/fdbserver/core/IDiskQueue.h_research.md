# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/IDiskQueue.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/IDiskQueue.h

Purpose: defines the abstract durable byte-queue interface used by log-like storage components and the version enum for disk queue page checksums.

Important APIs/types: `IDiskQueue::location`, virtual methods `initializeRecovery`, `readNext`, `getNextReadLocation`, `getNextPushLocation`, `read`, `push`, `pop`, `commit`, `getCommitOverhead`, `getStorageBytes`, trace/serialization helpers for `location`, `numeric_limits<IDiskQueue::location>`, and `DiskQueueVersion`.

Control flow and state: callers initialize recovery from a minimum location. If recovery is incomplete, they repeatedly call `readNext` until it returns less than requested bytes; after recovery, `readNext` must not be called again. `push` appends bytes and returns the end location; `pop` removes bytes before a location; `commit` makes prior pushes/pops durable, but crash before completion may persist any prefix of pushes/pops. `read(start,end,CheckHashes)` reads arbitrary ranges with optional hash checking.

State and persistence behavior: implementations persist a virtually infinite byte stream. `location` is effectively the sequence index with `hi` always zero and `lo` equal to the sequence, but serialization includes both fields for compatibility. `DiskQueueVersion` selects hashlittle, crc32, or xxhash3 page checksums.

Dependencies and integration: depends on FDB storage byte metrics, `IClosable`, Flow boolean params, serialization, traceability, and numeric limits. Transaction logs and spill/reference queues can implement or consume this abstraction.

Risks and tests: recovery protocol ordering is strict. Commit durability is prefix-based, so callers must tolerate partial persistence. Location comparison/limits must remain stable. Tests should cover recovery boundaries, read/push/pop ordering, crash during commit, hash versions, arbitrary reads, close behavior, and storage byte reporting.
