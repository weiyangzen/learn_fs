# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MoveKeys.h

## Purpose
`MoveKeys.h` declares data-distribution shard movement operations and storage-server add/remove helpers. It is the contract for updating system keyspace state during data movement.

## Important APIs, Types, And Functions
`MoveKeysLock` serializes ownership fields used to guard writes. `DDEnabledState` is an in-memory data-distribution mode gate with enabled, snapshot, and blob-restore-preparing states. `MoveKeysParams` bundles data move ID, one range or multiple ranges, destination teams, healthy destinations, flow locks, completion promise, remote flag, relocation interval, cancellation policy, and optional bulk-load task state. Actors include `readMoveKeysLock`, `takeMoveKeysLock`, `checkMoveKeysLock`, `rawStartMovement`, `rawFinishMovement`, `moveKeys`, `cleanUpDataMove`, `addStorageServer`, `removeStorageServer`, `canRemoveStorageServer`, and `removeKeysFromFailedServer`.

## Control Flow
DD takes the move-keys lock, starts movement by updating source/destination metadata, waits for fetch/ready conditions, then finishes movement and cleans old destinations. Removal paths check that no keys remain before deleting server metadata.

## State And Persistence Behavior
These functions mutate FoundationDB system keyspace: shard assignments, server lists, server keys, key servers, data-move metadata, and TSS mappings. `DDEnabledState` itself is process-local and resets on restart.

## Dependencies And Integration Points
It depends on commit transactions, key range maps, Native API, master types, seed shard initialization, storage interfaces, TSS mapping, and bulk-load task state. It is central to data distributor, storage recruitment, failed-server handling, bulk loading, and physical shard movement.

## Risks And Edge Cases
Overlapping moves, stale locks, multiple-range physical shard moves, TSS paired removals, remote DC movement, and DD-disabled modes are high-risk. `keys` and `ranges` are mutually exclusive by convention, so callers must enforce it.

## Test Signals
Simulation should verify lock conflict rejection, start/finish idempotence under retries, cancellation cleanup, failed-server metadata removal, storage-server add/remove versions, TSS mapping correctness, and no data loss during overlapping or retried movements.
