# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerSmallFile.java

## Purpose

`TestContainerSmallFile` exercises low-level container protocol calls for small writes and reads. It validates allocate/write/read behavior, invalid block/container errors, BCS ID handling, and echo RPC behavior through a real non-HA cluster.

## Important APIs, Types, And Functions

Setup creates `StorageContainerLocationProtocolClientSideTranslatorPB` and `XceiverClientManager`. Tests call SCM allocation and `ContainerProtocolCalls` for write/read/chunk and echo paths. Important types include `BlockID`, `ContainerWithPipeline`, `ContainerProtos`, `ByteString`, and `StorageContainerException`.

## Control Flow

Each test allocates or references a container, obtains an xceiver client for the pipeline, then performs protocol calls. Invalid-read tests intentionally use wrong block or container IDs and assert the expected exception/result. The BCS test writes and reads with block commit sequence IDs.

## State And Persistence Behavior

Successful tests create containers and block/chunk data on datanodes. BCS IDs are persisted in block/container metadata and affect read validation. Invalid tests should not mutate valid container state.

## Dependencies And Integration Points

The file integrates SCM allocation, xceiver client pooling, datanode container protocol, protobuf command responses, and Ozone container test helpers.

## Risks And Test Signals

Failures can indicate wire-protocol regressions, bad error mapping, BCS ID handling bugs, or client-manager lifecycle leaks. Low-level protocol tests are sensitive to pipeline readiness and datanode state.
