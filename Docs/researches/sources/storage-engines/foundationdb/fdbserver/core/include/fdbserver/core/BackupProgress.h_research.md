# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgress.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgress.h

Purpose: tracks backup progress by log epoch and tag, and computes unfinished backup ranges for log-router or range backup workers.

Important APIs/types: `BackupProgress`, `addBackupStatus`, `getUnfinishedPartitionedBackup`, `getUnfinishedRangePartitionedBackup`, `setBackupStartedValue`, `getEpochStatus`, and actor `getBackupProgress`.

Control flow and state: construction captures database ID and ascending epoch metadata. `addBackupStatus` merges worker progress by keeping the maximum saved version per tag. Unfinished backup calculation returns maps keyed by `(epoch, endVersion, tagCount)` to tag start versions, using epoch tag enumeration and adjusted begin/end versions. Private helpers update tag versions and remove completed tags. The object stores progress, epoch tag counts, and the raw `backupStartedKey` value decoded from system keyspace.

State and persistence behavior: the class itself is in-memory and reference-counted, but it represents backup progress persisted in system keyspace. `getBackupProgress` populates it from the database and reports through trace severity.

Dependencies and integration: depends on FDB types, `BackupProgressTypes`, arenas, and FastRef reference counting. It integrates with backup agents/workers determining which mutation log ranges still need upload.

Risks and tests: iteration order is explicitly significant. Off-by-one version math determines whether `[savedVersion + 1, endVersion)` gaps are backed up. Tests should cover multiple epochs, partially complete tags, missing progress, range-backup locality, backup started value, and duplicate worker statuses.
