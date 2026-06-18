# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineFollower.java

## Purpose
Concrete test class that runs the shared `TestContainerStateMachine` suite with `DivisionInfo.isLeader()` mocked as `false`, covering follower-side state-machine behavior.

## Important APIs, Types, And Functions
Extends `TestContainerStateMachine`; the constructor calls `super(false)`.

## Control Flow
JUnit discovers the inherited tests. Construction fixes the role flag before base `setup()` builds the mocked Ratis division.

## State And Persistence
No local state is introduced. All fixture state is inherited and in-memory.

## Dependencies And Integration Points
Depends on the base Ratis state-machine tests and shares the same dispatcher, state machine, and Ratis mocks.

## Risks And Edge Cases
Coverage depends entirely on inherited tests. Follower-specific paths not covered by the base suite remain untested.

## Test Signals
Inherited tests passing show failure propagation, timeout handling, and per-container unhealthy handling work when initialized as a follower.
