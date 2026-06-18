# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/StateMachine.java

## Purpose

`StateMachine<STATE, EVENT>` is a small reusable event-driven transition table for enum states and events. It stores an initial state, optional final states, and mappings from `(event, fromState)` to `toState`.

## APIs and control flow

Construction copies final states into an immutable set or uses an empty set. `addTransition(from, to, event)` inserts into a per-event map held in a Guava `LoadingCache`, which lazily creates `HashMap` instances. `getNextState(from, event)` looks up the target state and throws `InvalidStateTransitionException` when absent. Accessors expose initial and final states.

## State, dependencies, and integration

State is mutable transition maps plus immutable initial/final metadata. The class depends on Guava cache and immutable set utilities. It integrates with Ozone components that want declarative transition validation without building a component-specific state engine.

## Risks and test signals

The transition maps are mutable and not synchronized; callers should configure them before concurrent use. Final states are only stored, not enforced by `addTransition` or `getNextState`. Tests should cover transition lookup, absent events, null final-state input, duplicate transition replacement, and concurrency assumptions if used after startup.
