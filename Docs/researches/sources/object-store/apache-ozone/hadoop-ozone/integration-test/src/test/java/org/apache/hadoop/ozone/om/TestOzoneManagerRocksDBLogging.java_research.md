# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRocksDBLogging.java

## Purpose
Integration test for OM RocksDB logging configuration. It verifies that RocksDB log output is absent when disabled and appears after enabling logging and restarting OM.

## Important APIs and Types
The class `TestOzoneManagerRocksDBLogging` uses `OzoneConfiguration`, `RocksDBConfiguration`, `DBStoreBuilder.ROCKS_DB_LOGGER`, `GenericTestUtils.LogCapturer`, and `MiniOzoneCluster`. Key methods are `init`, `shutdown`, `testOMRocksDBLoggingEnabled`, `enableRocksDbLogging`, and `waitForRocksDbLog`.

## Control Flow
Each test starts a mini-cluster without datanodes after explicitly disabling RocksDB logging in the configuration. The test first asserts that waiting for a RocksDB log marker times out. It then toggles the config object to enable logging, restarts OM, and waits until captured logs contain the RocksDB implementation marker `db_impl.cc`.

## State and Persistence
The tested state is configuration-derived RocksDB logger behavior across OM restart. No Ozone object metadata is created. The `LogCapturer` is static and observes process-level logger output.

## Dependencies and Integration Points
This integrates OM DB initialization, `RocksDBConfiguration` serialization back into `OzoneConfiguration`, mini-cluster restart, and the HDDS RocksDB logger bridge.

## Risks and Edge Cases
The test is timing-sensitive because log emission depends on RocksDB startup internals. The captured marker is implementation-specific. Because the log capturer is static, earlier logs could affect repeated execution if not isolated by the initial timeout expectation.

## Test Signals
Passing confirms disabled RocksDB logging suppresses expected low-level RocksDB output and enabling the configuration takes effect after OM restart.
