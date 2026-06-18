# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/StateMachineReadyRule.java

Purpose: `StateMachineReadyRule` blocks SCM safe mode exit until the HA Ratis state machine has applied transactions and reported readiness. In non-HA or missing-state-machine cases, it validates immediately.

Important APIs and types: It extends `SafeModeExitRule<Boolean>`, subscribes to `SCMEvents.STATEMACHINE_READY`, and reads readiness through `SCMStateMachine.getIsStateMachineReady()`. `getStatusText()` reports the latest ready state or `NA`.

Control flow: The base `SafeModeExitRule.onMessage` drives validation. `validate()` returns the state machine readiness flag when a state machine exists and `true` otherwise. `process`, `cleanup`, and `refresh` are no-ops because the rule state lives entirely in the state machine.

State and persistence behavior: The class stores only a reference to `SCMStateMachine`. It has no persistence and no internal counters. Persistent HA state is managed by Ratis and the SCM state machine.

Dependencies and integration points: The rule is added by `SafeModeRuleFactory` only when SCM is a `StorageContainerManager` with an HA manager and Ratis server. It connects the safe mode event model to the Ratis leader readiness event.

Risks: If the state machine reference is null, safe mode does not wait for HA replay. If readiness is set prematurely elsewhere, this rule cannot detect incomplete application; it trusts `SCMStateMachine`.

Test signals: Tests should simulate `STATEMACHINE_READY` events with ready false and true, verify non-HA/null behavior validates, and confirm status text changes with the underlying state-machine flag.
