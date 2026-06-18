# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolume.java

Purpose: Abstract base class for datanode storage volumes. It centralizes VERSION-file lifecycle, volume state, storage directory paths, usage accounting, temporary directories, storage reports, and health checks.

Important APIs and types: Defines `VolumeType` and `VolumeState`. Core methods include `initialize`, `initializeImpl`, `format`, `createWorkingDir`, `createTmpDirs`, `getCurrentUsage`, `getReport`, `incrementUsedSpace`, `decrementUsedSpace`, `failVolume`, `shutdown`, `check`, `recordTimeoutAndCheckFailure`, and the generic nested `Builder`.

Control flow: Construction parses the configured storage location, creates the root if needed, configures `VolumeUsage`, initializes disk-check sliding windows, and sets initial state. `initializeImpl` analyzes the storage directory and either creates it, creates a VERSION file, reads an existing VERSION file, or fails on inconsistency. `check` verifies existence/permissions, optionally performs read/write disk checks, handles low-space bypasses, and marks failure only when the IO sliding window exceeds tolerance.

State and persistence: Persistent state is the VERSION file with storage ID, cluster ID, datanode UUID, creation time, and layout version. Runtime state includes `VolumeUsage`, current state, working/tmp/disk-check dirs, config, storage type, and sliding windows for IO and timeout failures.

Dependencies and integration points: Subclasses specialize data, metadata, and DB behavior. `StorageVolumeChecker` invokes `check` and `recordTimeoutAndCheckFailure`. `StorageLocationReport` is used for SCM heartbeats and reports. Permission setup uses `ServerUtils` and SCM config keys for data dirs.

Risks: VERSION state transitions are strict; a non-empty directory without VERSION is inconsistent. `shutdown` sets state to `NON_EXISTENT`, which is a lifecycle marker rather than a fresh disk analysis. Tests should cover all `analyzeVolumeState` branches, cluster/datanode/version validation, disk-check low-space behavior, timeout tolerance, and permission setting.
