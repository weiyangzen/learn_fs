# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerUtil.java

## Purpose
`KeyValueContainerUtil` creates container metadata/chunks/DB structures, reconstructs container metadata at startup, loads checksum/statistics state, detects empty containers, removes DB state, and stages deleted containers.

## Important APIs, Types, And Functions
Key methods are `createContainerMetaData`, `removeContainer`, `removeContainerDB`, `noBlocksInContainer`, `parseKVContainerData`, `getBlockLengthTryCatch`, `getBlockLength`, `isSameSchemaVersion`, `moveToDeletedContainerDir`, and `getTmpDirectoryPath`. Internal population helpers calculate pending deletes, block statistics, finalized blocks, and data checksum.

## Control Flow
Creation makes metadata and chunks directories and caches a schema v1/v2 DB store; schema v3 skips per-container DB creation. `parseKVContainerData` verifies descriptor checksum unless skipped, defaults missing schema to v1, locates DB files, opens DBs, populates pending deletes/delete txn ID/BCSID/block stats, creates a missing chunks dir, marks empty containers, loads checksum data, runs inspectors, and loads finalized block IDs. Removal deletes or uncaches DB state and moves the container directory to the deleted-container staging area.

## State And Persistence
It creates directories and old-schema DB stores, reads/writes RocksDB metadata, updates in-memory `KeyValueContainerData` statistics, may persist data checksum in metadata, removes schema-v3 KV rows, and renames container directories for deletion.

## Dependencies And Integration Points
It integrates `BlockUtils`, schema store implementations, `ContainerChecksumTreeManager`, `ContainerInspectorUtil`, `PendingDelete`, `KeyValueContainerMetadataInspector`, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.STORAGE_SPACE_DISTRIBUTION`, `DatanodeConfiguration`, and `HddsVolume`. It is used by startup, create, delete, import/export, and scanner/inspector flows.

## Risks And Test Signals
Risks include partial directory cleanup, missing DB behavior, stale metadata counters, checksum load warnings hiding issues, schema-v3 DB removal failures, and deleted-staging overwrites. Tests should cover startup reconstruction, missing metadata recalculation, legacy no-schema containers, pending-delete bytes before/after layout finalization, missing chunks-dir repair, finalized-block loading, no-blocks checks, and delete move failures.
