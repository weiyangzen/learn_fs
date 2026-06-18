# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerData.java

## Purpose
`KeyValueContainerData` is the in-memory metadata model for a key-value container and the data shape persisted into the `.container` YAML file. It extends `ContainerData` with key-value-specific paths, DB type, schema version, delete transaction tracking, block commit sequence ID, finalized blocks, and schema-aware DB key formatting.

## Important APIs and Types
Important getters/setters include metadata path, DB file, schema version, DB type, block commit sequence ID, and delete transaction ID. `buildContainerReplicaProto` creates datanode container reports. `getContainerReplicaProtoState` maps container protobuf states to SCM replica states. Finalized block APIs manage a concurrent set and `clearFinalizedBlock(DBHandle)` deletes finalized-block table entries. DB key APIs include `getBlockKey`, `getDeletingBlockKey`, `getLatestDeleteTxnKey`, `getBcsIdKey`, `getBlockCountKey`, `getBytesUsedKey`, `getPendingDeleteBlockCountKey`, `getPendingDeleteBlockBytesKey`, filters, `startKeyEmpty`, and `containerPrefix`.

## Control Flow
Construction initializes type, ID, layout, size, origin identifiers, delete transaction ID, and finalized block set. YAML field initialization extends base container YAML fields with metadata path, chunks path, DB type, and schema version. Counter update methods keep in-memory statistics and metadata table values aligned, using batch operations for delete accounting. Schema-aware formatting prefixes keys with the schema-v3 container key prefix and leaves schema-v1/v2 keys unprefixed.

## State and Persistence
The object itself is in memory, but many fields are persisted in `.container` YAML and metadata DB tables. `updateAndCommitDBCounters` and `resetPendingDeleteBlockCount` write RocksDB metadata table values. `deleteTransactionId` is monotonic via `max`. `finalizedBlockSet` is concurrent and cleared from both memory and DB during container close.

## Dependencies and Integration Points
`KeyValueContainer` owns this data object and delegates report/state/path behavior to it. Block managers, delete services, scanners, schema migration tools, and metadata inspector all use its schema-aware keys and filters. It integrates with `DatanodeSchemaThreeDBDefinition` for schema-v3 prefixes and `VersionedDatanodeFeatures` for storage-space-distribution metadata.

## Risks and Test Signals
Schema-aware key formatting is critical: using raw constants instead of helper methods can corrupt schema-v3 shared DB layouts. The copy constructor resets delete transaction ID to zero, which is safe only where callers expect a fresh metadata object. Counter updates subtract released bytes/counts and assume caller-provided values are consistent with in-memory statistics. Tests across `TestKeyValueContainer`, `TestBlockManagerImpl`, block deletion tests, schema compatibility/migration tests, and metadata inspector tests exercise these keys and counters.
