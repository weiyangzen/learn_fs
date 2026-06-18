# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSetDiskChecks.java

## Purpose
Verifies `MutableVolumeSet` startup disk-check behavior for data, metadata, and DB volumes, plus container/report handling when a volume fails.

## Important APIs, Types, And Functions
Uses `MutableVolumeSet.checkAllVolumes`, local `DummyChecker`, `ContainerSet.handleVolumeFailures`, `StorageVolumeUtil.getHddsVolumesList`, and key-value container creation utilities.

## Control Flow
Tests create configured data, metadata, and DB directories, assert dirs are created, use dummy checkers that fail some or all volumes, and run a volume-failure integration test that removes only the affected container and queues a full container report.

## State And Persistence
Temporary dirs, volume maps, failed lists, container metadata, missing-container sets, and queued SCM reports are mutated.

## Dependencies And Integration Points
Integrates volume checker, datanode `StateContext`, SCM report protobufs, key-value containers, Ozone container mocks, and randomized directory names.

## Risks And Edge Cases
Dummy checker fails volumes by iteration order. Report-count assertions depend on `StateContext` report generation behavior.

## Test Signals
Healthy/failed counts, directory existence, missing-container membership, container presence/absence, and report counts validate behavior.
