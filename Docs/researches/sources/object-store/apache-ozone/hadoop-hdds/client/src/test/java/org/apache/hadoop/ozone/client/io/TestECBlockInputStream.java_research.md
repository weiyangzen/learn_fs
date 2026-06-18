## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStream.java

**Purpose:** Tests direct EC block reads when enough data locations are available, including location sufficiency, per-replica block length calculation, reads across EC chunk boundaries, seeking, failure reporting, spare location fallback, pipeline refresh adaptation, and zero-byte-read handling.

**Important APIs/types/functions:** `setup()` uses EC 3-2 RS with 1 MiB cells. `testSufficientLocations()` checks when available data indexes are enough for small, full, and large blocks; parity-only reconstruction is not considered sufficient for direct reads. The block-size tests verify each per-index stream length for blocks shorter than one cell, spanning two/three cells, full stripes, and partial stripes. `testSimpleRead()`, `testSimpleReadUnderOneChunk()`, `testReadPastEOF()`, and `testReadCrossingMultipleECChunkBounds()` validate data ordering and EOF. Seek tests check EOF bounds, zero-length blocks, valid position mapping, and remaining bytes. Failure tests assert `BadDataLocationException` identifies failed datanodes and that spare same-index locations are tried before failing. `testEcPipelineRefreshFunction()` converts a refreshed EC pipeline to a single-node standalone pipeline for a specific replica index. `testZeroByteReadThrowsBadDataLocationException()` ensures a zero-byte short read throws rather than spinning.

**Control flow:** The stream maps logical block offsets to EC data indexes and per-index block streams. Reads pull data in EC cell order and update position. On direct-stream failures, it reports failed locations; if a spare location for the same replica index exists, it retries through another stream. Zero-byte reads are treated as inconsistent failure.

**State and persistence:** Uses synthetic pipelines, in-memory test streams, position counters, failure flags, and Ozone client config. No persistence.

**Dependencies and integration points:** Depends on `ECBlockInputStream`, `BadDataLocationException`, `ECStreamTestUtil`-like local test doubles, HDDS pipeline and datanode types, replication config, and JUnit.

**Risks:** Local `TestBlockInputStream` uses byte values based on stream creation order rather than actual EC data, so it validates ordering/position more than real content. Comments in the zero-byte test mention implementation requirements and signal a regression target.

**Test signals:** High-value signal for EC direct-read boundary math, error classification, and failover prerequisites used by `ECBlockInputStreamProxy`.
