# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainer.java

## Purpose
`KeyValueContainer` is the concrete datanode container implementation for Ozone key-value containers. It owns lifecycle transitions, on-disk directory and `.container` file creation/update, DB sync/compaction during close/export, import/export/copy workflows, scanner entry points, and synchronization around container metadata.

## Important APIs and Types
It implements `Container<KeyValueContainerData>`. Major APIs include `create`, `delete`, `hasBlocks`, `markContainerForClose`, `markContainerUnhealthy`, `markContainerForDelete`, `quasiClose`, `close`, `update`, `importContainerData`, `exportContainerData`, `copyContainerDirectory`, `scanMetaData`, `scanData`, and lock methods. It also exposes pending put-block cache methods and path helpers. It uses `KeyValueContainerData`, `VolumeSet`, `VolumeChoosingPolicy`, `ContainerPacker`, `DBHandle`, `BlockUtils`, and `KeyValueContainerUtil`.

## Control Flow
Creation takes the volume-set read lock, chooses a volume, reserves committed space, selects schema/path layout, verifies the container is new, creates metadata/chunks/DB directories, writes the YAML `.container` file through a temp file and atomic rename, and retries other volumes on general IO failures. Close/quasi-close first flush RocksDB WAL outside the write lock, reacquires the write lock, syncs again, updates state and the `.container` file, and clears pending put-block cache. Export takes the write lock, validates state, compacts/removes DB for non-schema-v3, downgrades to read lock while packing, and synchronizes schema-v3 dump generation with `dumpLock`. Import unpacks to a tmp/final destination, loads descriptor data, parses counters, rewrites local metadata, and cleans up partial data on failure.

## State and Persistence
Persistent state includes container directories, chunks directory, DB files, schema-v3 dump files, metadata tables, and the YAML `.container` descriptor. In-memory state includes a non-fair read/write lock, `dumpLock`, `pendingPutBlockCache`, and the config-derived empty-dir check flag. State transitions are persisted by `updateContainerFile`; failures generally restore the prior state unless the container has been marked UNHEALTHY.

## Dependencies and Integration Points
`KeyValueHandler` creates and manipulates these containers for client/container commands. `ContainerReader` reconstructs instances at startup. Replication/import/export paths use `ContainerPacker` and `ContainerImporter`. Data and metadata scanners call `scanMetaData` and `scanData`, which delegate to `KeyValueContainerCheck`. Disk balancer and replication tests construct instances directly. Schema handling integrates with `VersionedDatanodeFeatures` and `OzoneConsts.SCHEMA_V3`.

## Risks and Test Signals
This class has high persistence and concurrency risk. Atomic `.container` update failures call volume failure handling and may leave temp files. `hasReadLock()` appears to call `tryLock()` without unlocking, so it behaves like acquisition rather than ownership inspection. Import failure cleanup can move/delete local directories and remove schema-v3 DB rows. Export lock downgrading must avoid concurrent mutation while still permitting packing. Tests in `TestKeyValueContainer`, `TestKeyValueContainerMarkUnhealthy`, `TestTarContainerPacker`, replication/importer tests, container reader tests, scanner integration tests, and block/delete command tests provide broad signals.
