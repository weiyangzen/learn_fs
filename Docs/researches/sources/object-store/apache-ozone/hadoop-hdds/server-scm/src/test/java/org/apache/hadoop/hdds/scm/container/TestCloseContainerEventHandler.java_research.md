# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestCloseContainerEventHandler.java

## Purpose

This test class verifies `CloseContainerEventHandler`, which responds to SCM close-container events by transitioning container state and sending `CloseContainerCommand` messages to pipeline datanodes. It covers invalid containers, invalid states, delayed lease-based close, RATIS close, and EC force-close behavior.

## Important APIs, Types, and Functions

- `CloseContainerEventHandler.onMessage(ContainerID, EventPublisher)` is the handler under test.
- `ContainerManager.getContainer` and `updateContainerState` provide container metadata and state transition.
- `PipelineManager.getPipeline` provides target datanodes.
- `LeaseManager.acquire` optionally delays command publication.
- `CloseContainerCommand` and `CommandForDatanode` are captured from `SCMEvents.DATANODE_COMMAND`.
- `createPipeline` and `createContainer` build RATIS and EC fixtures.

## Control Flow and State Behavior

`setup` mocks container manager, pipeline manager, leader SCM context, event publisher, and lease manager. Invalid-container and already-closed tests confirm no datanode commands are fired. The lease-delay test puts a container in `CLOSING`, uses a real `LeaseManager` behind a mock wrapper, verifies no immediate command publication, then waits for delayed publication. Valid close tests use an OPEN container, mock `updateContainerState(FINALIZE)` to set it CLOSING, and verify one close command per pipeline node. EC containers are expected to use force close, while RATIS containers are not.

## State and Persistence

No durable storage is used. Container state is held in mutable `ContainerInfo` objects and changed by Mockito answers. Lease state is in memory and shut down after the delay test.

## Dependencies and Integration Points

The test connects container lifecycle state, pipeline membership, SCM leader gating, lease scheduling, and event publication. It uses `RatisReplicationConfig`, `ECReplicationConfig`, `Pipeline`, `CloseContainerCommand`, `LeaseManager`, and Mockito captors.

## Risks and Test Signals

Risks include sending close commands for invalid containers, duplicate or missing datanode commands, incorrect EC force flag, and timing flakiness in delayed close. Captured command assertions verify target DN set, container ID, pipeline ID, and force flag.
