## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SetNodeOperationalStateCommand.java

Purpose: `SetNodeOperationalStateCommand` asks a datanode to persist its current operational state, optionally with an expiry epoch.

Important APIs and types: it extends `SCMCommand<SetNodeOperationalStateCommandProto>`, uses `HddsProtos.NodeOperationalState`, exposes `getOpState()` and `getStateExpiryEpochSeconds()`, and supports `getFromProtobuf()`.

Control flow and state: construction requires explicit command id, operational state, and expiry seconds. `getProto()` writes all three values. `getFromProtobuf()` null-checks and preserves the command id, state, and expiry. The expiry value is zero for indefinite state according to the constructor documentation.

Persistence and integration: this command is transport state for SCM-to-datanode operational-state synchronization. The actual durable persistence is expected in datanode state storage, not here. It integrates with node maintenance, decommission, state transitions, and `StorageContainerDatanodeProtocolProtos`.

Risks and test signals: `opState` is not null-checked in the constructor; callers rely on protobuf builder or enum defaults to reject invalid state. The `stateExpiryEpochSeconds` field is mutable only within the class but is not final. There are no direct tests in this subset; integration tests should assert datanode-side persistence and expiry interpretation.
