# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolume.java

Purpose: Main datanode data-volume implementation for Ozone containers. It extends `StorageVolume` with container tracking, per-volume metrics, committed-space reservation, schema V3 RocksDB management, deleted-container cleanup, and volume-specific health checks.

Important APIs and types: Exposes `HDDS_VOLUME_DIR`, `TMP_CONTAINER_DELETE_DIR_NAME`, `VolumeIOStats`, `VolumeInfoMetrics`, container ID set operations, `incCommittedBytes`, `getCommittedBytes`, `loadDbStore`, `createDbStore`, `compactDb`, `checkDbHealth`, and helpers for container and DB directories. The nested builder fixes storage subdirectory `hdds`.

Control flow: Construction initializes metrics and then calls base initialization unless building a failed placeholder. `createWorkingDir` creates normal working directories and creates per-disk DB stores when schema V3 is finalized. `createTmpDirs` prepares the inherited tmp and disk-check directories plus the `deleted-containers` staging directory. `check` increments scan metrics, updates space/risk gauges, runs base directory/IO checks, and for schema V3 validates that the DB exists and can be opened read-only when RocksDB disk checking is enabled.

State and persistence: Persistent state includes inherited VERSION metadata, `<hdds>/<cluster>/current` container directories, temporary deleted-container directories, and optional per-volume `container.db` under either the HDDS volume or a selected `DbVolume`. Runtime state includes committed bytes, container IDs, DB loaded/failure booleans, DB parent directory, optional `DbVolume`, and metrics registrations.

Dependencies and integration points: `MutableVolumeSet` owns instances. Volume choosing policies mutate committed bytes. `DiskBalancerService` reads usage, increments/decrements space, and uses tmp directories. Schema V3 DB operations go through `HddsVolumeUtil`, `DatanodeStoreCache`, and `RawDB`. Container counts can be delegated to `ContainerController`.

Risks: DB lifecycle is sensitive to schema-finalization state, chosen DB volume, and whether `dbParentDir` has been initialized. `compactDb` assumes a non-null DB parent. Deleted-container cleanup is best-effort and logs failures without failing startup. Tests should cover schema V3 enabled/disabled behavior, DB load failure health checks, committed-byte accounting, SCM-HA container path fallback, cleanup of deleted-container tmp dirs, and shutdown unregistering metrics and closing DBs.
