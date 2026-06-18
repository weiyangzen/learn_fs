# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeStateManager.java

Purpose: unit tests for `NodeStateManager`, the internal state store and health transition engine used by `SCMNodeManager`.

Important APIs and types: setup creates a minimal `ConfigurationSource`, `SCMContext` with finalization complete by default, mocked `HDDSLayoutVersionManager`, and `MockEventPublisher`. Tests use `DatanodeDetails`, `DatanodeInfo`, `NodeStatus`, `HddsProtos.NodeState`, `SCMEvents`, `FinalizationCheckpoint`, `LayoutVersionProto`, and container IDs.

Control flow: tests add/retrieve nodes, count all/filtered nodes, mark nodes stale and dead based on heartbeat age, verify allowed health transitions and fired events, test resurrection through `HEALTHY_READONLY` before returning to `HEALTHY`, and validate layout-version/finalization behavior where lower-MLV datanodes become healthy-readonly only after SCM crosses `MLV_EQUALS_SLV`. Additional tests set operational state, add/remove container mappings, ensure changing op state re-emits the appropriate current health event, and update a node by UUID with new address, host, op state, and layout version.

State and persistence: all state is in-memory inside `NodeStateManager`, including node maps, statuses, heartbeat timestamps, known layout versions, and container sets. The mock publisher records events and payloads for assertions.

Integration points and risks: this is core safety coverage for node lifecycle, event publication, and upgrade finalization gating. Risks include the anonymous configuration returning null for all keys, so defaults from utility methods shape timeouts, and tests focus on single-node paths rather than high-concurrency updates.
