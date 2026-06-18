<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerShard.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerShard.h

## Purpose
`StorageServerShard.h` defines `StorageServerShard`, the compact representation of a continuous key range hosted by one storage server and its local assignment state.

## Important APIs, Types, and Functions
The main type is `StorageServerShard` with `ShardState` values `NotAssigned`, `Adding`, `ReadWritePending`, `ReadWrite`, `MovingIn`, and `Error`. Constructors capture range, creation version, actual shard ID, desired shard ID, state, and optional physical move metadata. Helpers include `notAssigned`, `getShardState`, `setShardState`, `getShardStateString`, `toString`, and `serialize`.

## Control Flow
Storage actors and management code construct shard objects when reporting shard state or mutating assignment status. State is stored internally as `int8_t`, converted to the enum by accessors, and serialized with range and ID metadata. `toString` formats range, IDs, version, state, and optional move-in shard ID for tracing.

## State and Persistence Behavior
The object is a serializable state record. It persists range ownership and creation/move metadata in messages or server-local structures, but this header does not perform storage writes. `version` records shard creation version, `id` records current shard ID, `desiredId` records intended shard ID, and `moveInShardId` links physical move metadata when present.

## Dependencies and Integration Points
It depends on `FDBTypes.h` for `KeyRange`, `Version`, and `UID`, plus Flow serialization. `StorageServerInterface.h` returns vectors of `StorageServerShard` through `GetShardStateReply`, and data distribution or physical shard movement code interprets the states.

## Risks and Edge Cases
`getShardState` trusts the stored `int8_t`; corrupt or future values stringify as `InvalidState`. Physical move states require callers to preserve `moveInShardId` consistently. Tests should catch transitions where `desiredId` diverges from `id` longer than intended.

## Test Signals
Shard assignment, physical shard move, recovery, wrong-shard, and data distribution tests are the main signals. Serialization round trips should preserve optional `moveInShardId` and all state enum values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerShard.h -->
