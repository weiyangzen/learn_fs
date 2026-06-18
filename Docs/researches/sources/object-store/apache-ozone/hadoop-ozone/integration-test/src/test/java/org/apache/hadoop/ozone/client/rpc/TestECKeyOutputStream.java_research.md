# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestECKeyOutputStream.java

## Purpose
`TestECKeyOutputStream` validates erasure-coded key output behavior: stream type selection, bucket default replication, overwrites between EC and RATIS, large single-write chunk striping, EC container metadata, datanode failure recovery, and unsupported hflush/hsync.

## Important APIs, types, and functions
The fixture uses a ten-datanode `MiniOzoneCluster`, `ECReplicationConfig(3,2,RS,chunkSize)`, one-megabyte chunks, small client buffer geometry, disabled checksum and flush delay, relaxed dead/stale/slowness/no-leader timeouts, allowed replication config regex, and enabled hsync flags. Key APIs include `ECKeyOutputStream`, `KeyOutputStream`, `OzoneBucket`, `BucketArgs`, `DefaultReplicationConfig`, `ContainerOperationClient`, `PipelineManager`, `ContainerID`, `Handler`, Mockito static mocking, and `GenericTestUtils.waitFor`.

## Control flow
Basic tests verify explicit EC key creation returns `ECKeyOutputStream`, creation without bucket defaults returns normal `KeyOutputStream`, and EC bucket defaults produce EC streams and readable data. Overwrite tests create a key under EC or RATIS configs and then overwrite it with the other replication type, asserting `OzoneKeyDetails.getReplicationConfig()` matches the latest write. A RATIS key can still be explicitly created in a bucket whose default is EC.

The single-write tests build buffers with optional offset and write 11, 13, 15, 20, or 21 chunks in one `write(byte[], offset, length)` call, then read back the exact selected range. The container metadata test closes existing EC pipelines, writes a fresh EC key, waits until SCM reports one key and five replicas for the container, and validates content. The datanode ID change test mocks `Handler.getDatanodeId()` to return a bogus ID once for replica index one, expects a new pipeline/location and the old container to close. The datanode-kill test shuts down the first node of the first EC pipeline mid-write, waits for flush checkpoint completion, verifies the next block group excludes the killed node, reads both copies back, and restarts the node. `testBlockedHflushAndHsync` asserts EC output rejects hflush and hsync with `NotImplementedException`.

## State and persistence behavior
The tests observe EC block-group location lists, pipeline IDs, replica indexes, SCM container key counts, replica counts, bucket default replication config, key replication config after overwrite, flush checkpoint state, and persisted readback content. They also validate recovery from pipeline/container replacement after datanode identity mismatch or node shutdown.

## Dependencies and integration points
This file integrates Ozone client EC streaming, OM bucket defaults and key metadata, SCM EC pipeline management, datanode handler identity, container operations CLI client, and read reconstruction. Mockito is used to inject a low-level datanode ID mismatch.

## Risks and test signals
`testECKeyCreatetWithDatanodeIdChange` is marked `@Unhealthy("HDDS-11821")` and has a typo in its method name. The class has a static initialization hazard: `inputSize` is initialized from `chunkSize` before `chunkSize` is assigned in `init()`, so it is initially zero unless later code relies on recalculated values elsewhere. Strong signals are exact content readback across multi-chunk EC writes, five replicas for a 3-2 EC container, new pipeline allocation after a mocked datanode ID mismatch, exclusion of a killed node from the next block group, and rejected hflush/hsync.
