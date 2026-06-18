# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneClient.java

## Purpose
`TestOzoneClient` is a network-free unit test suite for basic Ozone client operations over `RpcClient` using mock OM and datanode implementations.

## Important APIs, Types, And Functions
`init` creates a client with `SinglePipelineBlockAllocator`. `createNewClient` injects `MockOmTransport` and `MockXceiverClientFactory` into an anonymous `RpcClient`. `expectOmException` asserts OM exception result codes. Tests cover volume deletion, volume metadata/quota defaults, bucket creation timestamps, RATIS one-node key writes and reads, multi-write block allocation, and EC replication config writes with validation disabled and multi-node allocator.

## Control Flow
Tests create randomized volume/bucket/key names, execute public client APIs, then assert returned metadata, readback content, or expected exceptions. The EC test closes the default client, creates a special configuration with small block size and disabled replication validation, uses `MultiNodePipelineBlockAllocator`, writes EC keys, and verifies key metadata.

## State And Persistence Behavior
The test owns one `OzoneClient` and `ObjectStore` per test lifecycle. Persistent behavior is modeled by `MockOmTransport` maps and `MockDatanodeStorage`. Client close runs after each test.

## Dependencies And Integration Points
The suite exercises `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `RpcClient`, replication configs, mock allocators, and mock xceiver factory. It validates the public client facade against the mock protocol layer.

## Risks And Edge Cases
The mock OM omits many production validations and service metadata. The test writes strings created from zero byte arrays for allocation coverage, so content semantics are less meaningful there. EC validation is disabled intentionally to focus on client IO path rather than config policy.

## Test Signals
Provides broad smoke coverage for create/delete volume, create bucket, write/read key, block allocation on repeated writes, and EC key creation through the production `RpcClient` stream-building path.
