# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeChecker.java

## Purpose
Tests asynchronous `StorageVolumeChecker` behavior for single and bulk checks, failed volume removal, skipped scan metrics, Guava timeout semantics, and timeout tolerance.

## Important APIs, Types, And Functions
Exercises `StorageVolumeChecker.checkVolume`, `checkAllVolumes`, `shutdownAndWait`, `AsyncChecker`, local `DummyChecker`, `Futures.withTimeout`, `MutableVolumeSet.checkAllVolumes`, `OzoneContainer`, and `ContainerSet`.

## Control Flow
Parameterized tests cover all `VolumeCheckResult` values plus thrown exceptions. Volume deletion creates containers on a volume, deletes the volume directory, runs checks, and expects the volume and containers removed. Timeout tests block `check` with latches and verify first vs second timeout behavior.

## State And Persistence
Temporary Ozone container dirs and volume maps are created. Runtime state includes last-check timestamps, metrics counters, timeout windows, failed lists, and container maps.

## Dependencies And Integration Points
Integrates Guava futures, Hadoop disk checker exceptions, fake timers, Ozone container utilities, layout versions, datanode config, and key-value metadata paths.

## Risks And Edge Cases
Concurrency timeout tests are sensitive but bounded with latches. Guava exception behavior is dependency-sensitive. Filesystem deletion drives integration behavior.

## Test Signals
Delegate invocation counts, callback counts, failed set sizes, scan-skip metrics, removed containers, failed volume counts, captured `TimeoutException`, and timeout-failure recording validate behavior.
