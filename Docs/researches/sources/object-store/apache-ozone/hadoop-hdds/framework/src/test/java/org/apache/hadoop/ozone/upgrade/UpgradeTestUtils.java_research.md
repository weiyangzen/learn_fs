# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/UpgradeTestUtils.java

Purpose: Shared utilities for upgrade tests, including VERSION file creation and injected finalization executors.

Important APIs/types/functions: `createVersionFile`, `newPausingFinalizationExecutor`, `newTerminatingFinalizationExecutor`, `StorageInfo`, `HddsProtos.NodeType`, `InjectedUpgradeFinalizationExecutor`, and `UpgradeTestInjectionPoints`.

Control flow: `createVersionFile` builds `StorageInfo` with node type, random cluster ID, current time, metadata layout version, optional properties, then writes a `VERSION` file. Executor helpers configure injection callbacks that either pause on latches and resume or terminate by returning true.

State and persistence behavior: Writes VERSION files under caller-provided directories. Executor callbacks synchronize on provided latches and log state transitions.

Dependencies and integration points: Uses Ozone storage metadata, protobuf node types, Java properties, UUIDs, latches, and SLF4J.

Risks: Version file content includes current time and UUID, so exact file bytes are nondeterministic. Pausing executor must be unpaused or tests can hang.

Test signals: Enables deterministic upgrade storage setup and controlled finalization concurrency/failure tests.
