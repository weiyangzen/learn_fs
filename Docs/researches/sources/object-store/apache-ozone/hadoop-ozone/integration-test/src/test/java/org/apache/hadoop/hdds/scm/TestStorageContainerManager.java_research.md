# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManager.java

## Purpose

`TestStorageContainerManager` is a broad integration test for core SCM behavior: initialization, authorization, block deletion, datanode registration after reinitialization, topology-aware heartbeat processing, close-container command recovery, container-report queue behavior, and SCM info reporting.

## Important APIs, Types, And Functions

The class uses `MiniOzoneCluster`, `StorageContainerManager`, `SCMClientProtocolServer`, `SCMStorageConfig`, `DeletedBlockLog`, `SCMBlockDeletingService`, `NodeManager`, `ReplicationManager`, `EventQueue`, `FixedThreadPoolWithAffinityExecutor`, `ContainerReportHandler`, `IncrementalContainerReportHandler`, datanode stores, and Ratis group validation. Helpers configure topology/block deletion, create delete transactions, inspect datanode DB tables, validate Ratis storage, and locate container servers.

## Control Flow

The main `test` starts a cluster, runs block-deletion, RPC-permission, and heartbeat-topology checks, then stops/reinitializes SCM and verifies old datanodes react to mismatched cluster IDs. Separate tests cover deletion throttling, SCM initialization/failure/info, close-container commands after SCM restart, dropped full container-report events, long queue/execution metrics, and non-dropping incremental report queues.

## State And Persistence Behavior

This file exercises SCM storage directories, Ratis group directories, SCM DB metadata, OM key locations, deleted-block transaction logs, datanode block/delete transaction tables, node heartbeat timestamps, container lifecycle state, event queues, and command queues. Several tests deliberately restart, delete, or reinitialize SCM storage to validate persistence safeguards.

## Dependencies And Integration Points

It integrates SCM client protocol, security authorization, OM/key creation helpers, datanode heartbeat and report dispatch, block deletion service, topology mapping, replication manager, event framework, and datanode RocksDB schemas.

## Risks And Test Signals

Risks include broad test coupling, sleeps around asynchronous reports, and internal-state mocking. Failures are high-signal for SCM lifecycle, metadata persistence, delete-block processing, heartbeat/report backpressure, or admin authorization regressions.
