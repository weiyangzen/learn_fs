## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/ECStreamTestUtil.java

**Purpose:** Centralizes EC stream test fixtures: synthetic `BlockLocationInfo`/pipeline creation, deterministic data filling and validation, parity generation, index maps, and in-memory block stream factories with fault injection.

**Important APIs/types/functions:** `createKeyInfo()` builds closed pipelines with replica-index maps and block metadata. `zeroFill()` pads a buffer to its limit. `randomFill(ByteBuffer[], stripeSize, rand, length)` stripes random bytes across data buffers and finalizes limits; the single-buffer overload fills all remaining space. `assertBufferMatches()` validates buffer contents against a `SplittableRandom`. `generateParity()` normalizes data buffer positions/limits, zero-fills partial data buffers, invokes `CodecUtil.createRawEncoderWithFallback()`, and returns parity buffers. `createIndexMap()` creates random datanodes mapped to given EC indexes. `TestBlockInputStreamFactory` creates `TestBlockInputStream` instances by EC replica index and can fail selected indexes once. `TestBlockInputStream` reads from an injected `ByteBuffer`, supports seek, error on read, error on seek, and tracks EC replica index.

**Control flow:** Utilities are deterministic when callers reuse the same random seed. The factory maps requested single-node pipelines back to the current EC pipeline replica index, selects the corresponding data/parity buffer, optionally injects a first-read failure, and records created streams.

**State and persistence:** Holds in-memory maps/lists of streams, buffers, current pipeline, and fail-once indexes. `TestBlockInputStream` mutates buffer position as stream position. No persistence.

**Dependencies and integration points:** Depends on EC replication config, datanode/pipeline types, `BlockExtendedInputStream`, `BlockInputStreamFactory`, Ozone erasure-code raw encoders, and test random data. Used heavily by EC direct, proxy, reconstructed stream, and stripe tests.

**Risks:** Buffer position/limit manipulation is subtle; incorrect reset can invalidate later assertions. The test stream returns data from shared buffers, so callers must isolate or reset state between tests. Fault injection is simple and not thread-safe.

**Test signals:** Provides the foundation for validating EC reconstruction parity, read ordering, failover, and position semantics without a live cluster.
