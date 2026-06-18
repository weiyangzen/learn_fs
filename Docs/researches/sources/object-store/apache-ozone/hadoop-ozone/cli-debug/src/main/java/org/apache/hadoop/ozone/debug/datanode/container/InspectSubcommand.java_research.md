# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InspectSubcommand.java

Purpose: `InspectSubcommand` runs key-value container metadata inspection across all local replicas.

Important APIs and types: It extends `AbstractSubcommand`, uses parent `ContainerCommands`, `KeyValueContainerMetadataInspector`, `KeyValueContainerData`, `BlockUtils.getUncachedDatanodeStore`, and `DatanodeStore`.

Control flow: The command gets Ozone configuration, loads containers, creates an inspector in `INSPECT` mode, iterates all containers, skips non-key-value data, opens each container store read-only, processes metadata, and prints JSON. Per-container `IOException` is caught and printed to stderr with stack trace.

State and persistence behavior: It reads RocksDB/container metadata stores using uncached read-only handles. No mutation is intended.

Dependencies and integration points: It integrates datanode debug loading with the container metadata inspector used to validate key-value container DB consistency.

Risks: The command continues after individual failures, which is useful but can mix JSON stdout with stack traces on stderr. It assumes container data can be cast for key-value containers only.

Test signals: Inspector JSON per key-value container and explicit stderr failures for unreadable stores.
