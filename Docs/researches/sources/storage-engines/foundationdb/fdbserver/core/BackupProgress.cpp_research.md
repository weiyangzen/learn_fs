# sources/storage-engines/foundationdb/fdbserver/core/BackupProgress.cpp

## Purpose
Tracks persisted backup worker progress and computes unfinished backup ranges by epoch and tag. It also reads backup progress metadata from system keys into a `BackupProgress` object.

## Important APIs, Types, and Functions
- `BackupProgress::addBackupStatus()` records the max saved version per epoch/tag and validates total tag count per epoch.
- `updateTagVersions()` converts saved progress into next begin versions for unfinished tag ranges.
- `getUnfinishedPartitionedBackup()` and `getUnfinishedRangePartitionedBackup()` specialize `getUnfinishedBackup()` by locality.
- `getUnfinishedBackup(int8_t locality)` returns a map keyed by `(epoch, epochEnd, tagCount)` to tag begin versions needing work.
- `getBackupProgress()` transactionally reads `backupStartedKey` and `backupProgressKeys`.

## Control Flow
Progress is accumulated per worker status. To find unfinished work, the class enumerates expected tags for each epoch, adjusts overlapping epoch begin versions, consolidates previous-epoch saved progress when needed, and emits begin versions for incomplete or missing tags. `getBackupProgress()` repeatedly performs a system-key transaction and retries through `tr.onError()`.

## State and Persistence Behavior
In-memory state includes `progress`, `epochTags`, `backupStartedValue`, and `epochInfos`. Durable state is read from FoundationDB system keys, with `ACCESS_SYSTEM_KEYS`, `PRIORITY_SYSTEM_IMMEDIATE`, and `LOCK_AWARE` options. No writes are performed here.

## Dependencies and Integration Points
Depends on `BackupProgress.h`, NativeAPI transactions, backup system key encoders/decoders, `WorkerBackupStatus`, tag locality constants, and `EpochTagsVersionsInfo`. Used by backup recruitment logic to restart incomplete backup work after worker progress updates or recovery.

## Risks and Edge Cases
Epoch begin versions can overlap, so the code tracks `lastEnd` and adjusts begin versions to prevent duplicated work. Missing progress in newer epochs can be inferred from older epochs when recovery copied ranges. Tags from older epochs that do not exist in the current epoch are ignored. The system-key range read asserts it did not hit `TOO_MANY`.

## Test Signals
Embedded `/BackupProgress/Unfinished` validates active-backup detection, initial unfinished work, and advancing the next begin version after a saved worker status.
