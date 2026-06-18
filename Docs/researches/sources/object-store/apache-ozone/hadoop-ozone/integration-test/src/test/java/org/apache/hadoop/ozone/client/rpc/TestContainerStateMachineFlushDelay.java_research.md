# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFlushDelay.java

## Purpose
This class is a focused variant of the container state-machine corruption test with default flush-delay behavior and tiny buffer sizes. It verifies that deleting a container directory after an explicit flush still marks the container unhealthy when the stream closes.

## Important APIs, types, and functions
The setup enables block tokens and OM test secure mode, uses `CertificateClientTestImpl` and `SecretKeyTestClient`, configures fast reports/heartbeats, sets RATIS snapshot threshold one, and applies `ClientConfigForTesting` with `CHUNK_SIZE = 100`, `FLUSH_SIZE = 200`, `MAX_FLUSH_SIZE = 400`, and `BLOCK_SIZE = 800`. It uses `ContainerTestHelper.getFixedLengthString`, `KeyOutputStream`, `OmKeyLocationInfo`, and `FileUtil.fullyDelete`.

## Control flow
The single test creates a RATIS/ONE key, writes 110 bytes so the write exceeds one chunk, calls `flush()` to synchronize data under flush-delay behavior, writes a small `"ratis"` suffix, captures the single key location, deletes the container directory on the only datanode, and closes the stream through try-with-resources. It then asserts the datanode container state is `UNHEALTHY`.

## State and persistence behavior
Persistent state mutation is the container directory deletion. The test observes the in-memory container state after stream close. Small chunk sizing ensures the first write crosses a chunk boundary and exercises flush synchronization rather than only in-memory buffering.

## Dependencies and integration points
The test integrates secure MiniOzoneCluster setup, client buffer configuration, Ozone key writes, datanode container storage, and container state-machine failure detection. It is similar in spirit to `TestContainerStateMachine` but isolates flush-delay-sensitive behavior.

## Risks and test signals
The file relies on the default flush-delay setting described in comments rather than explicitly setting `setStreamBufferFlushDelay(true)`. The primary signal is exact `UNHEALTHY` state after deleting the active container path and closing the key.
