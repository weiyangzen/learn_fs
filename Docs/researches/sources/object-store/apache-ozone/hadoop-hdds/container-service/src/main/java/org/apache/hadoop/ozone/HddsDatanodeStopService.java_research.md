# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeStopService.java

## Purpose
Minimal callback interface for stopping an `HddsDatanodeService`.

## Important APIs, Types, And Functions
Single method `stopService()`.

## Control Flow
Implementers expose a stop hook that other components can invoke without depending on the concrete service class.

## State And Persistence
No state in the interface.

## Dependencies And Integration Points
Used as a decoupling point around datanode service lifecycle.

## Risks
The contract does not define idempotence, error handling, or close/join semantics, so implementers must document behavior.

## Test Signals
Signals are compile-time wiring and callers invoking stop without concrete datanode service dependencies.
