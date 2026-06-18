<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDispatcher.java

Purpose: bridge contract from transport/Ratis layers to concrete container handlers.

Important APIs and control flow: implementations dispatch protobuf commands with optional `DispatcherContext`, validate commands before Ratis execution, initialize and shut down metrics/services, build missing-container state from snapshot BCSIDs, look up handlers by container type, and propagate cluster ID. Default streaming methods throw unsupported operation exceptions unless overridden.

State and persistence: interface only. Implementations such as `HddsDispatcher` maintain handler maps, metrics, container set references, and state-context interactions.

Dependencies and integration: consumed by Xceiver/Ratis server paths and implemented by `HddsDispatcher`.

Risks and test signals: dispatcher implementations need tests for validation versus execution differences, handler lookup failures, lifecycle idempotency, streaming unsupported paths, and correct use of `DispatcherContext` during Ratis apply.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDispatcher.java -->
