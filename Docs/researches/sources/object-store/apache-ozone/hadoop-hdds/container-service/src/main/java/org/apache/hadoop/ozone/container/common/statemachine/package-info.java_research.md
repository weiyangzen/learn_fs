# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/package-info.java

## Purpose
Package documentation for the datanode state-machine package. It describes the container-service state flow as start through get-version, register, running, and shutdown, and notes that the state machine also handles command processing.

## Important APIs and Types
Important types in the package include `DatanodeStateMachine`, `StateContext`, `SCMConnectionManager`, `EndpointStateMachine`, queue metrics, MXBeans, and datanode configuration.

## Control Flow
At runtime, the state machine initializes SCM/Recon connections, advances endpoint states through version/register/heartbeat tasks, sends reports, receives SCM commands, and dispatches command handling.

## State and Persistence Behavior
Persistent side effects are delegated to runtime classes: datanode ID file persistence, layout-version storage, container state/metadata changes, and command ACK state. The package file itself has no state.

## Dependencies and Integration Points
This package is the bridge between HDDS datanode service lifecycle, SCM protocol endpoints, report publishing, command handlers, Ozone container storage, metrics, and JMX.

## Risks
The package comment is shorter than the current implementation and still mentions `GetVersion` and `Register` as package-level state flow while the datanode enum itself is `INIT/RUNNING/SHUTDOWN`; endpoint tasks carry the finer-grained endpoint states.

## Test Signals
Documentation consistency should be checked against the actual datanode and endpoint state enums when state transitions evolve.
