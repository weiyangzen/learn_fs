<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/RegisterEndpointTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/RegisterEndpointTask.java

## Purpose

`RegisterEndpointTask` registers a datanode with SCM after version negotiation. It sends datanode identity plus full node/container/pipeline reports, validates SCM's registration response, updates local datanode network identity when SCM supplies it, and advances the endpoint to heartbeat. The complete 286-line file was read.

## Important APIs, Types, and Functions

The class is final and implements `Callable<EndpointStateMachine.EndPointStates>`. Main APIs are `newBuilder()`, the `Builder` setters, `call()`, `getDatanodeDetails()`, and `setDatanodeDetails(DatanodeDetails)`. The visible-for-testing constructor accepts `EndpointStateMachine`, `OzoneContainer`, `StateContext`, and optional `HDDSLayoutVersionManager`.

## Control Flow

`call` first shuts down the endpoint if datanode details are absent. It locks the endpoint, runs only when the endpoint state is REGISTER, builds layout version information, fetches full container, node, and pipeline reports from `OzoneContainer`, then calls `rpcEndPoint.getEndPoint().register(...)`. The response is validated for datanode UUID, nonblank cluster ID, and success error code. Optional hostname/IP and network name/location from SCM are copied into `DatanodeDetails`. The endpoint then moves to its next state, missed heartbeats are reset, and heartbeat frequency is configured differently for passive endpoints versus SCM endpoints.

## State and Persistence Behavior

The class does not write persistent storage directly. It mutates endpoint state, endpoint missed heartbeat counters, datanode identity fields, and heartbeat frequency settings in `StateContext`. Persistent volume/container state is only read through report generation.

## Dependencies and Integration Points

It depends on SCM datanode protocol protobufs, `EndpointStateMachine`, `OzoneContainer`, `DatanodeDetails`, `StateContext`, and `HDDSLayoutVersionManager`. The registration reports couple it to `ContainerController`, node report construction, and pipeline server reporting.

## Risks and Edge Cases

SCM response validation is intentionally strict and can fail the task via Ratis `Preconditions`. IOException is logged but leaves the endpoint in REGISTER for retry. The builder requires a config argument but the built task does not otherwise use it, so tests should preserve the builder contract if refactoring. A null context is checked but the error message says container is missing, which can obscure diagnostics.

## Test Signals

Tests should cover missing datanode shutdown, successful register response advancing to heartbeat, SCM-supplied hostname/IP/network update, passive and active heartbeat frequency configuration, invalid cluster ID/error code/UUID failures, and IOException retry semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/RegisterEndpointTask.java -->
