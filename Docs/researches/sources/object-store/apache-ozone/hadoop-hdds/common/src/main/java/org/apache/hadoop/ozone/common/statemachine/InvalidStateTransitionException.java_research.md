# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/InvalidStateTransitionException.java

## Purpose

`InvalidStateTransitionException` is the typed failure thrown when a generic Ozone state machine receives an event that has no transition from the current state.

## APIs and control flow

The constructor records the current state and event, both as `Enum<?>`, and builds a message in the form `Invalid event: <event> at <state> state.`. `getCurrentState()` and `getEvent()` expose the stored values.

## State, dependencies, and integration

State is immutable by convention but the fields are not declared `final`. The class has no external dependencies. It integrates with `StateMachine.getNextState`, which throws it for missing transition table entries.

## Risks and test signals

Because state and event are stored as raw enums, consumers must know the concrete enum types from context. Tests should verify thrown messages and accessors for missing transitions, and ensure valid transitions do not allocate or throw.
