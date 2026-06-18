# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineStream.java

## Purpose
`TestContainerStateMachineStream` verifies the ByteBuffer streaming write path around the chunk-size boundary. It ensures data written through `OzoneDataStreamOutput` updates container `bytesUsed` for sizes one byte below and one byte above the configured chunk size.

## Important APIs, types, and functions
This abstract non-HA test uses an externally supplied `cluster()`. It creates volume/bucket state through `ObjectStore`, writes stream keys with `TestHelper.createStreamKey`, unwraps `KeyDataStreamOutput` from `OzoneDataStreamOutput.getByteBufStreamOutput()`, and resolves the target datanode with `TestHelper.getDatanodeService`. Data generation uses `ContainerTestHelper.generateData`.

## Control flow
`setup()` reads `OZONE_SCM_CHUNK_SIZE_KEY`, creates a client, and creates a test bucket. The parameterized test runs with offsets `-1` and `+1`, deriving sizes `chunkSize - 1` and `chunkSize + 1`. For each size, it creates a RATIS stream key, writes a `ByteBuffer`, flushes, captures key location info, closes the stream, then reads the corresponding datanode container's `bytesUsed`.

## State and persistence behavior
The state under observation is datanode container accounting, not file content. The assertion allows `bytesUsed` to be greater than the test size because the container may already include previous data. The test therefore proves at least that the streaming write path accounts for the new bytes.

## Dependencies and integration points
The file covers the streaming client API, byte-buffer output implementation, RATIS stream key creation, OM key location propagation, and datanode container data accounting. It complements the normal `OzoneOutputStream` tests.

## Risks and test signals
Because it only asserts `bytesUsed >= size`, it does not prove exact accounting or readback content. Its useful signal is boundary coverage around chunk size for the streaming state-machine path and successful propagation of location info from `KeyDataStreamOutput`.
