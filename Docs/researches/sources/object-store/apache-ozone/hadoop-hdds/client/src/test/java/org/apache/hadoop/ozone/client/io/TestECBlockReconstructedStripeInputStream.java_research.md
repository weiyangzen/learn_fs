## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedStripeInputStream.java

**Purpose:** Tests stripe-level EC reconstruction across full and partial stripes, missing data/parity combinations, recovery-index output selection, spare locations, failed-location exclusion, seek alignment, insufficient-location failures, and byte buffer pool edge cases.

**Important APIs/types/functions:** `recoveryCases()` enumerates no-recovery, one missing index, two data missing, data+parity missing, and parity-only recovery sets. `polluteByteBufferPool()` preloads larger buffers to guard against HDDS-7304-style assumptions about exact buffer capacity. `testSufficientLocations()` validates quorum logic with padding indexes, failed datanodes, and recovery index counts. `testReadFullStripesWithPartial()` parameterizes recovery cases over three full stripes plus a partial stripe and validates output buffer contents/positions. Partial-stripe tests cover one-, two-, and three-chunk final stripes, parity recovery, and multiple location maps. `testErrorThrownIfBlockNotLongEnough()`, `testErrorReadingBlockContinuesReading()`, and `testAllLocationsFailOnFirstRead()` assert `InsufficientLocationsException` in unrecoverable cases. `testNoErrorIfSpareLocationToRead()` verifies spare same-index replicas are used. `testSeek()` validates stripe-aligned seeking and remaining counts. `testSeekToPartialOffsetFails()` asserts non-stripe-aligned seek rejection. `testFailedLocationsAreNotRead()` ensures pre-marked failed datanodes are excluded from stream creation.

**Control flow:** The stripe stream chooses readable indexes, fills missing data/parity buffers, performs raw erasure decoding when recovery indexes are set or data indexes are missing, advances underlying streams one EC chunk per stripe, and updates logical block position. It refuses recovery when fewer than data-count usable locations remain or when requested seek positions are not stripe aligned.

**State and persistence:** Uses in-memory data/parity buffers, mutable recovery indexes, failed datanode sets, current position, buffer pool contents, and executor threads. No persistence.

**Dependencies and integration points:** Depends on `ECBlockReconstructedStripeInputStream`, `ECBlockInputStream` sufficiency semantics, `ECStreamTestUtil`, Ozone erasure coding, Hadoop `ByteBufferPool`, executor service, datanode/pipeline metadata, AssertJ, and JUnit.

**Risks:** This is a complex test matrix; failures can be caused by buffer position/limit mistakes as much as reconstruction logic. `polluteByteBufferPool()` highlights a real integration risk where pooled buffers may be larger than requested. Seek only supports stripe offsets, which is a documented limitation tested here.

**Test signals:** Very high signal for EC reconstruction correctness and failure handling, especially for partial stripes and degraded-location scenarios.
