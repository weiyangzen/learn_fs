# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/LeaderAppendLogEntryGenerator.java

## Purpose
Freon/Vapor generator that configures a standalone datanode as a Ratis leader and sends async Ozone write-chunk commands through `XceiverClientRatis`.

## Important APIs, types, and functions
Command `lalg`, options for pipeline id, chunk size, and next index. Extends `BaseAppendLogGenerator`. Uses `RaftClient` group management, `XceiverClientRatis`, `Pipeline`, `DatanodeDetails`, `ContainerCommandRequestProto`, `CreateContainerRequestProto`, `WriteChunkRequestProto`, `DatanodeBlockID`, in-flight queue, and metrics timer.

## Control flow
`call` initializes in-flight queue, config, random payload, server id, fake follower peer, plaintext Ratis stub, Freon state, and optionally configures a Ratis group. After a startup sleep, it creates a single-node Ratis pipeline, connects an xceiver client, creates container 1, then Freon operations send async write-chunk commands and remove in-flight IDs when futures complete.

## State and persistence behavior
Creates container and chunk data on the target datanode through normal xceiver/Ratis paths. Maintains in-flight step IDs but does not explicitly close the xceiver client in this source.

## Dependencies and integration points
Exercises datanode Ratis leader path, Xceiver client pipeline construction, Ozone container command protobufs, and Freon metrics.

## Risks and edge cases
Fake follower peers use duplicate IDs with different addresses. The `nextIndex` option only gates group configuration and is otherwise unused. Container id is hard-coded to 1, which can collide with existing state.

## Test signals
No direct tests. Runtime signals are create-container response, async future completions, in-flight queue behavior, and `append-entry` timer metrics.
