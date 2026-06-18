## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedInputStream.java

**Purpose:** Tests the higher-level reconstructed EC block stream that wraps stripe-level reconstruction, ensuring normal stream APIs work across multiple stripes, partial final stripes, unbuffering, byte-at-a-time reads, byte-array reads, EOF, and seek.

**Important APIs/types/functions:** `createStripeInputStream()` builds an `ECBlockReconstructedStripeInputStream` with synthetic block info, current pipeline, elastic buffer pool, executor, and checksum-enabled config. Metadata tests validate `getLength()` and `getBlockID()`. `testReadDataByteBufferMultipleStripes()` reads a block containing three full stripes plus a partial chunk, checks deterministic data, EOF, then seeks to zero and reads again after buffers were freed. `testReadDataWithUnbuffer()` calls `unbuffer()` after each read. `testReadDataByteBufferUnderBufferSize()` validates small-block reads. `testReadByteAtATime()` and `testReadByteBuffer()` cover single-byte and byte-array APIs. `testSeek()` performs repeated random seeks and validates content from each new position, then asserts seeking past EOF fails.

**Control flow:** The wrapper asks the stripe stream for reconstructed stripe buffers, copies data into caller buffers according to current position, releases/reacquires buffers on EOF or unbuffer, and delegates seek to stripe-aligned reconstruction as needed.

**State and persistence:** Uses deterministic random seed state, in-memory data/parity buffers, an elastic byte buffer pool, and a fixed thread pool executor shut down after each test. No persistence.

**Dependencies and integration points:** Depends on `ECBlockReconstructedInputStream`, `ECBlockReconstructedStripeInputStream`, `ECStreamTestUtil.generateParity`, Hadoop `ByteBufferPool`, executor services, and EC replication config.

**Risks:** Executor cleanup is explicit; missing shutdown would leak threads. Random seek iterations improve coverage but can produce variable failing positions. Elastic pool behavior is not bounded in this test class.

**Test signals:** Strong end-to-end unit signal for reconstructed EC stream compatibility with standard `InputStream` and `ByteBufferReadable` style APIs.
