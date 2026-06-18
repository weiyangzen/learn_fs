<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/HddsDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/HddsDispatcher.java

Purpose: datanode container command dispatcher bridging transport/Ratis requests to container-type handlers while enforcing tokens, state rules, space checks, metrics, audit, close actions, and scan triggers.

Important APIs and control flow: `dispatch` wraps `dispatchRequest` in `OzoneProtocolMessageDispatcher`. The request path records metrics by command/stage, validates tokens when requested by `DispatcherContext`, handles Ratis snapshot BCSID bookkeeping, rejects writes to missing containers, implicitly creates key-value containers for write/put paths when absent, rejects missing non-create operations, checks volume space and queues close actions, obtains the handler, invokes `handler.handle`, records latency, marks containers unhealthy on non-ignorable write failures, triggers scans, updates Ratis BCSID maps after `PutBlock`/`PutSmallFile`, and emits audit events. `validateContainerCommand` is the leader-side preflight for Ratis log creation. Streaming methods route direct data-channel and read-only stream operations to handlers.

State and persistence: dispatcher owns handler map, cluster ID propagation, protocol metrics, slow-operation threshold, token verifier, and references to `ContainerSet` and `StateContext`. It indirectly persists container creation, unhealthy state, and BCSID updates through handlers and container data.

Dependencies and integration: integrates with all container command protobufs, `Handler`, `ContainerSet`, `StateContext`, Ratis `DispatcherContext`, audit infrastructure, OpenTelemetry spans, token verifier, metrics, and volume set.

Risks and test signals: tests should cover implicit creation conditions, EC replica index propagation, missing-container rejection, token failure mapping, close action deduplication, volume-full write rejection, unhealthy marking only for non-ignorable failures, BCSID map updates, audit parameters, and slow-operation units. `streamDataReadOnly` mixes millisecond timing with nanosecond threshold naming, so performance audit expectations need care.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/HddsDispatcher.java -->
