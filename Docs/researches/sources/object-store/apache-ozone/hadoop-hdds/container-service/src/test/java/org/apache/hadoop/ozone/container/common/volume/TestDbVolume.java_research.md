# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestDbVolume.java

## Purpose
Tests `DbVolume` initialization, restart discovery of Hdds volume IDs, and DB-store cache cleanup when a DB volume fails.

## Important APIs, Types, And Functions
Uses `DbVolume.Builder`, `format`, `createWorkingDir`, `getHddsVolumeIDs`, `failVolume`, `StorageVolumeUtil.getVersionFile`, and singleton `DatanodeStoreCache`.

## Control Flow
Tests unformatted and formatted DB volume states, create cluster subdirectories to simulate DB instances and rebuild on restart, then create three Hdds DB stores on a DB volume and call `failVolume` to assert cache cleanup.

## State And Persistence
VERSION files, cluster directories, and DB instance directories are real temp filesystem state. `DatanodeStoreCache` is shared in-memory process state.

## Dependencies And Integration Points
Integrates Schema V3 setup, data and DB volume sets, storage type defaults, and SCM data directory configuration.

## Risks And Edge Cases
Cache cleanup assumes no unrelated DB handles remain in the singleton. Static configuration changes must not leak between tests.

## Test Signals
Storage state, cluster ID, storage type, VERSION presence, discovered ID count, and cache size validate lifecycle behavior.
