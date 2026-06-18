# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneContainerUpgradeShell.java

## Purpose
`TestOzoneContainerUpgradeShell` validates the offline repair command `datanode upgrade-container-schema` for upgrading a datanode's container schema after a schema-v2 container has been created and the datanode is moved to schema-v3 configuration.

## Important APIs, Types, and Functions
Setup configures short SCM/DN heartbeat and report intervals, sets replication-manager interval, disables `CONTAINER_SCHEMA_V3_ENABLED`, starts a mini cluster, and creates a client. The test writes a key, closes its container, switches one DN config to schema v3, restarts that DN, writes persisted DN details with `IN_MAINTENANCE`, stops the cluster, and runs `OzoneRepair` with `datanode upgrade-container-schema` and `-D ozone.metadata.dirs=...`.

## Control Flow, State, and Persistence
The flow creates an old-schema container, closes it through SCM, restarts a datanode with schema v3 enabled so its local container data needs upgrade, persists maintenance state to the datanode ID file, shuts down cluster services and caches, then runs the offline upgrade command with confirmation input. Persistent state includes datanode metadata directories, container RocksDB stores, datanode ID file operational state, and container cache/metrics cleanup.

## Dependencies and Integration Points
This integrates client key writes, OM key lookup, SCM container close, datanode restart/config mutation, persisted datanode details, container schema feature flag, repair CLI, metadata directory discovery, container caches, metrics, and RocksDB leak checks.

## Risks and Test Signals
Risks include offline command requiring full cluster shutdown, schema assumptions, cache leakage, and maintenance-state prerequisites. The main signal is exit code zero from the upgrade command after realistic old-schema container creation and shutdown.
