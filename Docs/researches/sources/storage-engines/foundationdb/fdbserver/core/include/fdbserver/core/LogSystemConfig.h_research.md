# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogSystemConfig.h

## Purpose
`LogSystemConfig.h` models the active and historical transaction-log topology for a database recovery generation, including TLogs, log routers, backup workers, locality policy, epoch boundaries, and compatibility metadata.

## Important APIs, Types, And Functions
`OptionalInterface<T>` stores a stable `UID` plus optional full endpoint interface. `TLogSet` describes one DC/locality set of TLogs, log routers, backup workers, anti-quorum, replication factor, policy, localities, `TLogVersion`, and tag locations. `OldTLogConf` captures prior generations. `LogSystemConfig` stores current sets, old sets, log-router/tag counts, epoch, recruitment ID, locked TLog IDs, and range-backup tags, with helpers such as `allLocalLogs`, `allPresentLogs`, `hasTLog`, `hasLogRouter`, `hasBackupWorker`, and `getEpochEndVersion`.

## Control Flow
Recovery code builds a new `LogSystemConfig`, compares it with previous generations, recruits/logs roles based on its sets, and publishes it via `ServerDBInfo` and coordinated state. Optional interfaces can be compared by identity even when endpoints are absent.

## State And Persistence Behavior
This is persisted cluster metadata in coordinated state and broadcasts. Serialization gates `rangeBackupWorkerTags` for non-FlatBuffer archives using `protocolVersion().hasRangeBackupWorker()` while FlatBuffers always include all fields.

## Dependencies And Integration Points
It depends on backup and TLog interfaces, replication policies, and `DatabaseConfiguration`. It is consumed by master recovery, cluster controller recruitment, TLogs, log routers, backup/range-backup workers, and workers receiving `ServerDBInfo`.

## Risks And Edge Cases
Serialization compatibility is the dominant risk. Identity-only equality must not hide endpoint changes when communication availability matters. Old generations and known locked logs must be retained long enough for recovery safety.

## Test Signals
Important signals are log-system serialization across protocol versions, equality/identity comparisons, recovery generation transitions, all-present/all-local log enumeration, and downgrade/upgrade tests around range-backup worker tags.
