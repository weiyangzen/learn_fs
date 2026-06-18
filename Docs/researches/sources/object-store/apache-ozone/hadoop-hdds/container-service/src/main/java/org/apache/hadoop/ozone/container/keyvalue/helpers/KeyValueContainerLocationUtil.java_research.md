# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerLocationUtil.java

## Purpose
`KeyValueContainerLocationUtil` computes canonical filesystem locations for key-value container base directories, metadata directories, chunks directories, and DB files.

## Important APIs, Types, And Functions
Public methods are `getContainerMetaDataPath`, `getChunksLocationPath`, `getBaseContainerLocation`, and `getContainerDBFile`. Private `getContainerSubDirectory` shards container IDs with `(containerId >> 9) & 0xFF`.

## Control Flow
Given volume dir, cluster ID, and container ID, it builds `<volume>/<cluster>/current/<containerDir>/<containerId>`, then appends metadata or chunks names. DB path selection is schema-aware: schema v3 uses the volume DB parent and `CONTAINER_DB_NAME`; older schemas use `<metadata>/<containerId>.db`.

## State And Persistence
The class does not create files but defines the persistent path contract used by creation, startup loading, tar packing, deletion, and DB caching.

## Dependencies And Integration Points
It depends on `OzoneConsts`, `Storage`, `KeyValueContainerData`, and volume DB-parent configuration. It is used by `KeyValueContainer`, `KeyValueContainerUtil`, `TarContainerPacker`, and DB helpers.

## Risks And Test Signals
Risks include path contract drift, negative IDs, null schema-v3 DB parent, and sharding mismatches with existing disks. Tests should cover base/meta/chunks path construction, old and schema-v3 DB file selection, and null/negative validation.
