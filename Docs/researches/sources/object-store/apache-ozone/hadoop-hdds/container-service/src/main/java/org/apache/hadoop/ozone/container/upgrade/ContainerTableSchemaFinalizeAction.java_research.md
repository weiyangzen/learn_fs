# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ContainerTableSchemaFinalizeAction.java

Purpose: upgrade-finalization action that migrates witnessed-container metadata from a previous table definition into the current protobuf-value table.

Important APIs and functions: annotated with `@UpgradeActionHdds(feature = WITNESSED_CONTAINER_DB_PROTO_VALUE, component = DATANODE)`. `execute` obtains the datanode's `WitnessedContainerMetadataStore`, gets the previous `containerIdsTable` and current `CONTAINER_CREATE_INFO_TABLE_DEF`, truncates the current table, iterates previous entries, writes them into the current table using a batch operation, and commits. `truncateCurrentTable` computes first and last keys and uses `deleteRange` plus a final delete for the exclusive end.

Control flow and state: the action is intended to be idempotent after crashes; it clears current data before copying from the previous table. Batch commit is the persistence boundary for the migration copy.

Dependencies and integration: invoked by `DataNodeUpgradeFinalizer` through HDDS layout feature actions. It depends on RocksDB table APIs, `ContainerID`, and witnessed-container metadata definitions.

Risks and test signals: delete range semantics and key ordering are important. Tests should cover empty current table, single-entry current table, multi-entry truncation, previous-table copy, crash/retry idempotence, and codec/RocksDB exceptions.
