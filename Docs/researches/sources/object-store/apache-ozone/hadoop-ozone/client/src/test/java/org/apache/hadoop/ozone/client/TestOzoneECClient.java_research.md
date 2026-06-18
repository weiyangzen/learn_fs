# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneECClient.java

## Purpose
`TestOzoneECClient` is a comprehensive network-free suite for EC write/read behavior through the real Ozone client stream stack with mock OM and datanodes. It targets data/parity layout, bucket default EC config, partial stripes, block group metadata, retry behavior, exclusion rules, and preallocated block handling.

## Important APIs, Types, And Functions
Fixture fields define a 3 data / 2 parity EC layout with 1024-byte chunks, reusable input chunks, `MockXceiverClientFactory`, `MultiNodePipelineBlockAllocator`, `MockOmTransport`, and a raw RS encoder. `createNewClient` injects mocks into `RpcClient`. `writeIntoECKey` overloads create volume/bucket/key and write byte arrays with optional bucket default replication config. `validateContent`, `getMatchingStorage`, `getAllLocationInfoList`, and `waitForFlushingThreadToFinish` support assertions.

Tests cover data-node stored data, parity data matching the RS encoder, readback content, default bucket EC replication, single-write calls containing many chunks and offsets, chunks smaller than chunk size, block group length metadata in put-block, committed key info ordering and data size, several partial-stripe cases, 10+4 EC partial stripe overflow regression coverage, node failure behavior, stripe-write retries, failed/closed datanode exclude list contents, large writes with mid-stream failures, partial chunk retry on close, and preallocated-block discard preventing retry exhaustion.

## Control Flow
Most tests create a bucket, write EC data through `bucket.createKey`, close the stream, then inspect mock datanode storage, mock OM committed key metadata, or read content back. Failure tests write an initial stripe, wait for the flush thread to pass a checkpoint, inject datanode failures through `MockXceiverClientFactory`, continue writing, and then assert block group counts and content. Retry-specific tests configure max retry counts or cluster sizes to assert success, `IOException`, or `IllegalStateException`.

## State And Persistence Behavior
State is shared across each test instance fields but reset by JUnit lifecycle and client close. Mock OM stores volumes, buckets, open keys, and committed keys. Mock datanode storages store per-node bytes and block metadata. The allocator's sliding cursor determines which mock nodes receive successive block groups.

## Dependencies And Integration Points
The suite integrates `RpcClient`, `ECKeyOutputStream`, `OzoneOutputStream`, `OzoneInputStream`, `OzoneBucket`, EC replication configs, raw erasure encoder, mock OM/datanode layers, stream internals such as `BlockOutputStreamEntry` and `BlockStreamAccessor`, and client config keys such as block size and max EC stripe write retries.

## Risks And Edge Cases
The tests rely on deterministic ordering of `DatanodeDetails` and allocator nodes. They inspect stream internals and mock storage internals, so refactors can break tests without changing public behavior. Some key sizes passed to `createKey` are approximate or smaller than actual written content in retry/partial tests, reflecting current stream behavior rather than strict declared-size enforcement. Failure modeling is narrower than production because writes fail at mock storage and networking/pipeline state is simplified.

## Test Signals
This is the strongest signal in the subset for EC client correctness. It verifies data and parity bytes, EOF behavior, partial stripe padding, block group length metadata, key-location ordering, retry limits, exclude-list policy distinguishing failed vs closed containers, and correct reads after reallocation to new block groups.
