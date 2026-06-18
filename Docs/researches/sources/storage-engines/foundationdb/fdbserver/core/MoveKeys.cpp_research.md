# sources/storage-engines/foundationdb/fdbserver/core/MoveKeys.cpp

## Purpose
`MoveKeys.cpp` implements the core system-key transactions and coordination logic used by FoundationDB data distribution to add/remove storage servers and move key ranges between teams. It supports both legacy logical key movement (`keyServers` src/dest lists with boolean `serverKeys`) and shard-encoded location metadata (`DataMoveMetaData`, shard ids in `keyServers` and `serverKeys`, checkpoints, and bulk-load data moves). The file is heavily actor-based and is designed to tolerate retries, concurrent DD generations, removed storage servers, TSS mappings, and simulation fault injection.

## Important APIs, types, and functions
- `DDEnabledState` tracks in-memory DD enablement states: enabled, snapshot, and blob-restore-preparing. Its `trySet*` methods enforce UID ownership of transitions.
- `MoveKeysLock`, `readMoveKeysLock`, `takeMoveKeysLock`, `checkMoveKeysLock`, and `checkPersistentMoveKeysLock` coordinate exclusive DD ownership through `moveKeysLockOwnerKey` and `moveKeysLockWriteKey`.
- `moveKeys`, `rawStartMovement`, `rawCheckFetchingState`, and `rawFinishMovement` select logical versus shard-encoded move paths based on `SERVER_KNOBS->SHARD_ENCODE_LOCATION_METADATA`.
- Logical movement is handled by `startMoveKeys`, `checkFetchingState`, and `finishMoveKeys`.
- Shard-encoded movement is handled by `startMoveShards`, `finishMoveShards`, `checkDataMoveComplete`, `cleanUpDataMove`, `cleanUpDataMoveCore`, `cleanUpDataMoveBackground`, and `cleanUpSingleShardDataMove`.
- Storage server membership is handled by `addStorageServer`, `canRemoveStorageServer`, `removeStorageServer`, and `removeKeysFromFailedServer`.
- Helper paths include `removeOldDestinations`, two overloads of `unassignServerKeys`, `additionalSources`, `pickReadWriteServers`, `addReadWriteDestinations`, `waitForShardReady`, and metadata audit helpers.

## Control flow
The high-level data move sequence is `moveKeys`: sort destination team, start movement, start a fetching-state signal actor, finish movement, then defensively set `dataMovementComplete`. In the logical path, `startMoveKeys` reads overlapping `keyServers` ranges in bounded KRM batches, extends source lists with healthy read-write destinations when needed, sets the destination team in `keyServers`, removes stale destination ownership from `serverKeys`, and marks the new destinations as owning the range. `finishMoveKeys` rereads the same metadata, waits for destination storage servers and optionally TSS pairs to become readable at the transaction read version, then clears `dest` and promotes the destination team to source ownership.

The shard-encoded path persists a `DataMoveMetaData` record. `startMoveShards` creates or resumes metadata, validates conflicting data moves, optionally creates RocksDB checkpoints for physical moves, writes destination shard ids into `keyServers`, writes data-move shard ids into destination `serverKeys`, and can bind a bulk-load task to the data move. `finishMoveShards` waits for destination readiness, promotes destination servers into `keyServers` source ownership, updates every involved `serverKeys` range, deletes checkpoints, clears the data-move record, and completes a bulk-load task when present. Partial KRM pages are handled by shrinking the active range and looping.

## State and persistence behavior
The file mutates FDB system keyspaces: `keyServersPrefix`, per-server `serverKeysPrefixFor`, `serverListKeyFor`, `serverTagKeyFor`, `serverTagHistoryRangeFor`, `tagLocalityListKeyFor`, `serverMetadataKeys`, `serverMetadataChangeKey`, `moveKeysLock*`, `dataMoveKeyFor`, checkpoint keys, TSS mapping and quarantine keys, and bulk-load task ranges. Most transactions use `PRIORITY_SYSTEM_IMMEDIATE` and `ACCESS_SYSTEM_KEYS`; lock-sensitive paths also use `LOCK_AWARE`. KRM updates use `krmSetRangeCoalescing` or `krmSetPreviouslyEmptyRange` to maintain coalesced range maps.

Persistence invariants are symmetric: `keyServers` and `serverKeys` must agree about ownership, and shard-encoded moves must keep `DataMoveMetaData` phase/range/checkpoint state aligned with KRM entries. Physical moves create pending checkpoint metadata and later clear it through `deleteCheckpoints`.

## Dependencies and integration points
The code integrates with `fdbclient/SystemData.h` KRM encoders, `ManagementAPI` for DD mode changes, `StorageServerInterface` RPCs (`getShardState`), `TSSMappingUtil`, `BulkLoadUtil`, `ReadYourWritesTransaction`, `TxnCounters`, and Flow actor primitives. It is called by data distribution when recruiting, moving, or removing shards and is also used by failure handling when removing keys from failed servers.

## Risks and edge cases
Major risks are split-brain DD ownership, partial KRM pages, stale server lists, conflicts with existing data moves, transaction retry storms, and inconsistent location metadata. The lock protocol protects against overlapping DD generations by comparing previous owner/write IDs and self-conflicting writes. `finishMoveKeysBackoff` adds capped jittered exponential backoff for `transaction_too_old`. The audit helpers can detect `keyServers`/`serverKeys` corruption and set DD mode to security mode. Removed destination servers throw `move_to_removed_server`; conflicting physical moves are either cleaned up or cancelled depending on policy. TSS readiness is best effort and eventually skipped to avoid blocking production data movement.

## Test signals
There is a direct `TEST_CASE("/fdbserver/MoveKeys/finishMoveKeysBackoff")` validating the backoff envelope and retry knob. Many `CODE_PROBE` and `buggify` points exercise multi-transaction paths, retries, removed servers, and injected `transaction_too_old`. Trace events such as `RelocateShard_StartMoveKeys*`, `RelocateShard_FinishMoveKeys*`, `StartMoveShards*`, `FinishMoveShards*`, `CleanUpDataMove*`, and `CheckLocationMetadata*` are the main runtime/debug signals.
