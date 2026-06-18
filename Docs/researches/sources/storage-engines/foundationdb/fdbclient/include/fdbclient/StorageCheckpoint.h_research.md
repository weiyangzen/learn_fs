# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageCheckpoint.h

## Purpose
`StorageCheckpoint.h` declares metadata structures for storage checkpoints and data moves. These structs describe checkpoint format, state, covered ranges, source servers, serialized engine-specific checkpoint data, application action IDs, and data movement phases.

## Important APIs, Types, And Functions
- Constants `checkpointBytesSampleFileName` and `emptySstFilePath` name metadata artifacts.
- `CheckpointFormat` covers invalid format, RocksDB column-family export checkpoints, RocksDB filesystem checkpoints, and key-value checkpoints.
- `CheckpointMetaData` stores version, ranges, format, source server IDs, checkpoint ID, state, optional bytes sample file, serialized checkpoint payload, optional action ID, and directory.
- `CheckpointMetaData` helpers get/set state and format, set/get serialized checkpoint data, test range/key coverage, compare by checkpoint ID, stringify, and serialize.
- `std::hash<CheckpointMetaData>` hashes by checkpoint ID.
- `DataMoveMetaData` stores data move ID, version, ranges, priority, source/destination server sets, checkpoint IDs, phase, mode, and optional bulk load task state.
- `DataMoveMetaData` helpers get/set phase, stringify, and serialize.

## Control Flow And State
Checkpoint metadata progresses through pending, complete, deleting, and fail states. Data moves progress through prepare, running, completing, and deleting phases. Coverage helpers iterate stored ranges to answer whether a range or key is represented. Serialization packs every field needed to reconstruct metadata over the wire or from system storage.

## Persistence And External State
These structs are explicitly metadata for persistent storage/data movement workflows. They are serializable and likely stored in system keys or sent to storage servers. `serializedCheckpoint` carries engine-specific metadata understood by the corresponding key-value store. `bulkLoadTaskState` links data moves to bulk load tasks.

## Dependencies And Integration Points
It depends on `BulkLoading.h` and `FDBTypes.h`. It integrates with `NativeAPI.actor.h` checkpoint creation/lookup helpers, storage servers, data distribution, data movement, RocksDB checkpoint export/create flows, and bulk loading.

## Risks And Edge Cases
The include guard has a spelling typo (`FDBCLIENT_STORAGCHECKPOINT_H`), which is harmless if consistent but easy to duplicate incorrectly. `format`, `state`, and `phase` are stored as integer fields, so invalid casts are possible if unvalidated data is deserialized. Equality and hash only consider checkpoint ID, not covered ranges/version. Coverage helpers require full containment, not overlap. Serialized checkpoint payload lifetime and arena ownership must be preserved.

## Test Signals
Tests should cover serialization round trips, state/format/phase casts, range and key coverage, equality/hash behavior, string output with optional fields, checkpoint lifecycle transitions, data move lifecycle transitions, bulk load task linkage, invalid enum values from deserialization, and interactions with checkpoint creation/metadata lookup actors.
