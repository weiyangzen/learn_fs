# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestFileChecksumHelper.java

## Purpose
`TestFileChecksumHelper` verifies replicated and EC file checksum helper behavior, including empty block handling, one-block checksum fetches, cached checksum usage, and checksum computation after writing a real key through the mock client stack.

## Important APIs, Types, And Functions
`init` creates an `OzoneClient` with CRC32C checksum config, `MockOmTransport`, and `MockXceiverClientFactory`. `omKeyInfo` builds synthetic `OmKeyInfo` with RATIS or EC replication and optional cached checksum. `checksumHelper` selects `ReplicatedFileChecksumHelper` or `ECFileChecksumHelper`. `pipeline` builds a closed pipeline. `testEmptyBlock` and `testOneBlock` run for EC and RATIS. `buildValidResponse` creates a mocked datanode `GetBlock` response with chunk checksum data and EC stripe checksum when needed. `testPutKeyChecksum` writes a real key and computes its replicated checksum.

## Control Flow
For synthetic tests, Mockito supplies OM lookup results and xceiver responses. Helpers call `compute`, then tests inspect `getFileChecksum` and `getKeyLocationInfoList`. The real-key test writes data through `bucket.createKey`, constructs `ReplicatedFileChecksumHelper`, computes, and asserts CRC type and location count.

## State And Persistence Behavior
Synthetic tests have mocked state only. The real-key test persists volume/bucket/key metadata in `MockOmTransport` and chunk/block data in `MockDatanodeStorage`. Client state is closed after each test.

## Dependencies And Integration Points
It integrates checksum helper classes with `RpcClient`, `OzoneManagerProtocol`, `XceiverClientFactory`, `XceiverClientGrpc`, OM key-location metadata, datanode block checksum protobufs, and Hadoop checksum classes `MD5MD5CRC32FileChecksum` and `MD5MD5CRC32GzipFileChecksum`.

## Risks And Edge Cases
`buildValidResponse` uses artificial checksum bytes and does not validate against real data content. Empty-block tests expect MD5MD5CRC32 gzip checksum and null location list for negative length; changing helper semantics affects these assertions. The EC path depends on stripe checksum presence in chunk info.

## Test Signals
The parameterized tests cover both RATIS and EC helper selection. They assert empty-block checksum type, one-block location discovery, cached checksum handling, and real mock-stack checksum behavior with CRC32C.
