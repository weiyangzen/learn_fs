# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestSCMConnectionManager.java

## Purpose
`TestSCMConnectionManager` verifies that removing an SCM server unregisters the endpoint from the manager without mutating the endpoint state's lifecycle value.

## Important APIs, Types, And Functions
- `SCMConnectionManager.addSCMServer`, `removeSCMServer`, `getValues`, and `close` are used.
- `EndpointStateMachine.setState` and `getState` are used to set and verify `HEARTBEAT`.

## Control Flow
The test creates a connection manager in try-with-resources, adds one SCM address, obtains the created endpoint, sets its state to `HEARTBEAT`, removes the SCM server, and asserts the manager has no endpoints while the removed endpoint object still reports `HEARTBEAT`.

## State And Persistence Behavior
State is in-memory endpoint registration and endpoint state. There is no persistence.

## Dependencies And Integration Points
The test depends on `OzoneConfiguration`, `SCMConnectionManager`, `EndpointStateMachine`, and Java `InetSocketAddress`. It protects connection-manager behavior used by datanode endpoint state transitions.

## Risks And Edge Cases
The covered edge case is removal being mistaken for endpoint shutdown. This matters if external code still observes an endpoint object after removal.

## Test Signals
Signals are manager collection emptiness and preserved endpoint state equality.
