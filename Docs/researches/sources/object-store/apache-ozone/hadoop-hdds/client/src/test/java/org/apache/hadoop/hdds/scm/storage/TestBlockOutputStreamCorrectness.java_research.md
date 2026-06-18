## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockOutputStreamCorrectness.java

**Purpose:** Verifies that `BlockOutputStream` writes exactly the bytes supplied by callers for different write granularities, and that EC reconstruction `executePutBlock` remains compatible with chunks lacking `stripeChecksum`.

**Important APIs/types/functions:** `test(int writeSize)` parameterizes writes of 1 byte, 1 KiB, and 1 MiB over a 256 MiB random data buffer, repeating ten blocks through a `RatisBlockOutputStream`. `createBlockOutputStream()` configures `BufferPool`, `OzoneClientConfig`, `StreamBufferArgs`, and a mocked `XceiverClientManager` returning `MockXceiverClientSpi`. `MockXceiverClientSpi.sendCommandAsync()` asserts every `WriteChunk` payload byte matches the static `DATA` sequence and returns successful `PutBlock` responses with committed length. `testMissingStripeChecksumDoesNotMakeExecutePutBlockFailDuringECReconstruction()` constructs an EC pipeline for parity index 5 and calls `ECBlockOutputStream.executePutBlock(true, true, length, blockData)` using `BlockData` chunks without stripe checksum.

**Control flow:** The correctness test writes through buffering, flush, commit, and close paths; mock responses make the stream believe each async command succeeded. The EC test drives the reconstruction put-block branch and asserts no exception.

**State and persistence:** Uses static 256 MiB random data and per-client counters/indices to compare write order. No persistent output. Metrics are acquired through `ContainerClientMetrics`.

**Dependencies and integration points:** Integrates with Ratis and EC block output stream code, `BufferPool`, stream buffer configuration, container protobuf requests/responses, `ContainerClientMetrics`, and Ozone client versioning.

**Risks:** The large static data array and repeated writes are memory/time intensive for a unit test. The mock client validates payload order but does not simulate partial failures, retries, or real Ratis commit timing. Metrics acquired in helpers are not explicitly released in the test body.

**Test signals:** Strong byte-for-byte write-path signal across buffering sizes and a targeted compatibility signal for EC stripe-checksum schema evolution.
