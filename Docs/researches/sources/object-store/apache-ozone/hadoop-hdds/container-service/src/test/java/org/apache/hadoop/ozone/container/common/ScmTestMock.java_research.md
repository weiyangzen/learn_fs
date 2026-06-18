## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ScmTestMock.java

Purpose: `ScmTestMock` is an in-memory `StorageContainerDatanodeProtocol` implementation used by datanode tests.

Important APIs and state: it tracks RPC count, heartbeat count, container report count, command status report count, cluster ID, SCM ID, optional response delay, per-datanode container reports, per-datanode node reports, command status reports, and queued SCM command responses. Public methods expose counters, aggregate container/key/bytes-used counts, reset state, and mutate queued SCM commands and IDs.

Control flow: `getVersion()` increments RPC count, optionally sleeps, and returns version, SCM ID, and cluster ID. `sendHeartbeat()` increments RPC and heartbeat counts, records command status reports, optionally sleeps, and returns queued SCM command protos with the heartbeat datanode UUID. `register()` records node and container reports, optionally sleeps, and returns a successful registration protobuf with a generated cluster ID and datanode UUID.

Persistence and integration: all state is in memory. It integrates with live PB RPC through `SCMTestUtils`, datanode endpoint tests, SCM command delivery tests, and report aggregation assertions.

Risks and test signals: maps keyed by `DatanodeDetails` require consistent equality semantics. Raw `Map` usage in `updateContainerReport` bypasses generic checks. `register()` returns a random cluster ID rather than the mock's configured `clusterId`, which may be intentional for older tests but is surprising. Response delay simulates slow SCM calls.
