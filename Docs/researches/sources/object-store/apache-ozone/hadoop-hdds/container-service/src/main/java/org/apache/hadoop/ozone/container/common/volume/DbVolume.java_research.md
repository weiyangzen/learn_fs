# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/DbVolume.java

Purpose: Represents a datanode volume dedicated to per-HDDS-volume container database storage. Its on-disk layout is rooted under a `db` storage directory, with per-cluster and per-HDDS-storage-ID subdirectories containing `container.db`.

Important APIs and types: Extends `StorageVolume`; exposes `DB_VOLUME_DIR`, `addHddsDbStorePath`, and `getHddsVolumeIDs`. The nested `Builder` fixes the storage subdirectory name to `db`.

Control flow: Construction delegates base volume initialization, initializes an empty `hddsDbStorePathMap`, and scans existing database store paths when the volume is not a failed placeholder. `initializeImpl` extends normal `StorageVolume` initialization, then calls `scanForDbStorePaths`. Failure and shutdown both close cached DB handles.

State and persistence: Persistent state is the inherited VERSION file and the directory tree under `<db volume>/db/<clusterID>/<hddsStorageID>/container.db`. Runtime state is a map from HDDS volume storage IDs to DB store paths. `scanForDbStorePaths` rebuilds that map from disk when the volume is normal and the cluster directory exists.

Dependencies and integration points: Uses `DatanodeStoreCache.removeDB` to close RocksDB instances. `HddsVolume.createDbStore` registers newly created DB paths with the chosen `DbVolume`.

Risks: The map is a plain `HashMap`, so external concurrent mutations would need higher-level synchronization. `scanForDbStorePaths` trusts every child directory under the cluster directory to represent an HDDS volume storage ID. Tests should cover unformatted volumes, missing cluster dirs, listFiles failure, fail/shutdown closing all mapped DBs, and restart scanning of existing DB stores.
