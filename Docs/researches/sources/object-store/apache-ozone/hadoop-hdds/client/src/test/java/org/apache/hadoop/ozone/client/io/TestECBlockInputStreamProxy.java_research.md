## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStreamProxy.java

**Purpose:** Tests `ECBlockInputStreamProxy` dispatch between direct EC reads and reconstructed reads, position/remaining metadata, EOF behavior, failover after bad data locations, and seek behavior across stream replacement.

**Important APIs/types/functions:** `testExpectedDataLocations()` validates expected data indexes as a function of block length for EC 3-2 and 6-3. `testAvailableDataLocations()` counts available data indexes from pipeline replica indexes. Metadata tests assert block ID, length, position, and remaining. `testCorrectStreamCreatedDependingOnDataLocations()` checks whether the factory is invoked with `missingLocations=false` for direct reads or `true` for reconstruction. `testCanReadNonReconstructionToEOF()` and `testCanReadReconstructionToEOF()` read deterministic random data to EOF in both modes. `testCanHandleErrorAndFailOverToReconstruction()` injects a mid-read `BadDataLocationException`, verifies the caller buffer is effectively rewound by matching the same data sequence, and asserts failed datanodes are passed to the reconstruction factory. `testCanSeekToNewPosition()` verifies seeks on the active stream, fallback when direct seek fails, and failure when reconstructed seek also fails.

**Control flow:** On construction or first use, the proxy chooses direct or reconstruction based on location availability. During reads, a `BadDataLocationException` from the direct stream causes creation of a reconstruction stream with failed datanodes and continuation from the prior logical position. Seek delegates to the current stream and can trigger mode change on failure.

**State and persistence:** Tracks active stream mode, logical position, failed locations, and deterministic in-memory data. No persistence.

**Dependencies and integration points:** Uses `ECBlockInputStreamProxy`, `ECBlockInputStreamFactory`, `BlockExtendedInputStream`, `ECStreamTestUtil.TestBlockInputStream`, pipelines, replication config, and JUnit/AssertJ.

**Risks:** The test factory keys streams by boolean `missingLocations`, so repeated creations in the same mode overwrite the map entry. It verifies proxy-level behavior without real parity reconstruction.

**Test signals:** Strong signal for the proxy’s key responsibility: seamless direct-to-reconstruction failover while preserving user-visible stream semantics.
