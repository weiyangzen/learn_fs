# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/SinglePipelineBlockAllocator.java

## Purpose
`SinglePipelineBlockAllocator` is a deterministic one-node block allocator for simple client unit tests. It models block allocation without SCM by returning sequential blocks in one stable pipeline.

## Important APIs, Types, And Functions
The constructor stores `OzoneConfiguration`. `allocateBlock` lazily creates a one-member pipeline from `KeyArgs` replication type/factor and EC config when applicable, reads the configured SCM block size, and returns one `KeyLocation` with container ID 1 and sequential local ID.

## Control Flow
On first allocation it builds and caches the pipeline. Every call then creates a new `KeyLocation` for the next `blockId`. `ExcludeList` is accepted by the signature but ignored.

## State And Persistence Behavior
State consists of `blockId`, cached `pipeline`, and configuration reference. There is no durable persistence.

## Dependencies And Integration Points
It implements `MockBlockAllocator` for `MockOmTransport`, uses HDDS/Ozone protobufs, and is the default allocator for most non-EC mock-client tests.

## Risks And Edge Cases
Ignoring `ExcludeList` makes it unsuitable for failure/retry tests. It reuses the first replication settings for the cached pipeline; subsequent calls with different replication args will still use the original pipeline.

## Test Signals
`TestOzoneClient`, `TestBlockOutputStreamIncrementalPutBlock`, and checksum tests use this allocator through `MockOmTransport` for basic RATIS-style writes and reads.
