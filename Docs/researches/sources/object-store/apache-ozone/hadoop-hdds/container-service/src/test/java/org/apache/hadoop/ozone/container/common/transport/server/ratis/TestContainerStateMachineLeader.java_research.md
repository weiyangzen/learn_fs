# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineLeader.java

## Purpose
Concrete test class that runs the shared `TestContainerStateMachine` suite with `DivisionInfo.isLeader()` mocked as `true`, covering leader-side state-machine behavior.

## Important APIs, Types, And Functions
Extends `TestContainerStateMachine`; the constructor calls `super(true)`.

## Control Flow
JUnit executes inherited tests after construction sets the role flag. Base setup reports the mocked division as leader.

## State And Persistence
No local persistent or mutable state exists beyond the inherited fixture.

## Dependencies And Integration Points
Depends on the abstract state-machine suite and its Ozone/Ratis mock integrations.

## Risks And Edge Cases
The class has no independent assertions. Gaps in the base test scenarios apply here.

## Test Signals
Inherited tests passing indicate failure, timeout, and container-specific unhealthy behavior hold when the state machine sees itself as leader.
