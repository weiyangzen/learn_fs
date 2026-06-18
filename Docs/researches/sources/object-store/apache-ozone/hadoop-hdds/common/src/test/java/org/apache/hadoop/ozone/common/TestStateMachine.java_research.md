# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestStateMachine.java

## Purpose
Tests generic `StateMachine` transition behavior with local enum states and events.

## Important APIs, types, and functions
- Defines local `STATES` and `EVENTS` enums.
- Uses `StateMachine`, `InvalidStateTransitionException`, and set utilities.
- Test case is `testStateMachineStates`.

## Control flow
The test builds a state machine with allowed transitions, exercises valid transitions, checks final states, and asserts invalid transitions throw the expected exception.

## State and persistence behavior
State is in-memory current-state tracking inside the state machine. No persistence.

## Dependencies and integration points
The generic state-machine utility can be reused by Ozone lifecycle components.

## Risks and test signals
A broken transition table can allow invalid lifecycle transitions or reject valid ones. This test signals core transition enforcement.
