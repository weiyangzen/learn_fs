<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerInspector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerInspector.java

Purpose: optional startup/debug tool interface for inspecting or repairing containers.

Important APIs and control flow: `load` activates inspector behavior from configuration, `unload` disables it, `isReadOnly` declares whether `process` mutates containers, and `process` handles one container plus its `DatanodeStore`. The contract explicitly permits parallel processing across containers and requires implementations to batch log output and be thread-safe across calls.

State and persistence: interface only. Implementations may persist repairs to container metadata stores or only log diagnostics depending on read-only status.

Dependencies and integration: used during datanode startup/container loading workflows. Operates on `ContainerData` and `DatanodeStore`.

Risks and test signals: mutating inspectors are high-risk and need tests for idempotency, parallel execution, per-container serialization, and recovery from store errors. Read-only inspectors should prove they do not change metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerInspector.java -->
