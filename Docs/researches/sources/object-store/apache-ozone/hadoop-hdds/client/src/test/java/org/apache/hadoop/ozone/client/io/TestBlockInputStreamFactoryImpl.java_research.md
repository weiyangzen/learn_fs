## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBlockInputStreamFactoryImpl.java

**Purpose:** Verifies `BlockInputStreamFactoryImpl` selects the correct concrete block input stream type for Ratis/non-EC, streaming-read-enabled, and EC replication configs.

**Important APIs/types/functions:** `testNonECGivesBlockInputStream(boolean)` parameterizes `streamReadBlockEnabled`; for Ratis THREE it expects `StreamBlockInputStream` when enabled and `BlockInputStream` otherwise, while preserving block ID and length. `testECGivesECBlockInputStream()` expects `ECBlockInputStreamProxy` for `ECReplicationConfig(3,2)`. Local `createKeyLocationInfo()` helpers build closed pipelines with random datanodes and replica indexes.

**Control flow:** The factory branches on replication config type first, then on non-EC stream-read configuration. Tests instantiate the selected stream but do not perform reads.

**State and persistence:** Uses transient `OzoneConfiguration` and synthetic `BlockLocationInfo`. No persistence.

**Dependencies and integration points:** Integrates with `BlockInputStreamFactoryImpl`, `BlockInputStream`, `StreamBlockInputStream`, `ECBlockInputStreamProxy`, HDDS replication configs, pipelines, and `OzoneClientConfig`.

**Risks:** The test spies pipeline replica index for non-EC path but does not validate client factory/token/refresh propagation. It verifies type selection, not operational behavior.

**Test signals:** Clear regression signal for factory dispatch when stream read support or EC support changes.
