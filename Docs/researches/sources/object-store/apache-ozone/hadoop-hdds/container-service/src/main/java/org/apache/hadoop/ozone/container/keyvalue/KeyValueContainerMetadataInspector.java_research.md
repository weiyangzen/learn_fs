# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerMetadataInspector.java

## Purpose
`KeyValueContainerMetadataInspector` is an opt-in container inspector for diagnosing and optionally repairing aggregate metadata in key-value container DBs. It emits JSON reports showing stored DB metadata, recomputed aggregate values, chunks-directory status, and detected mismatches.

## Important APIs and Types
The inspector implements `ContainerInspector`. Modes are `REPAIR`, `INSPECT`, and `OFF`, controlled by the system property `ozone.datanode.container.metadata.inspector` or constructor injection. Main APIs are `load`, `unload`, `isReadOnly`, `process`, `inspectContainer`, `getDBMetadataJson`, `getAggregatePendingDelete`, and schema-specific pending-delete counters. Reports are logged to `ContainerMetadataInspectorReport`.

## Control Flow
`load` validates the system property once and enables inspect/repair or disables the inspector. `process` no-ops in OFF mode, verifies the container is `KeyValueContainerData`, builds JSON from DB metadata, recomputed block/byte aggregates, pending delete aggregates, and chunks directory info, then calls `checkAndRepair`. Repairable mismatches include block count, used bytes, pending delete block count, pending delete bytes when the layout feature is finalized, and missing chunks directory. In INSPECT mode repair actions are recorded as not repaired; in REPAIR mode the metadata table or filesystem is updated.

## State and Persistence
The class holds only the current mode. In REPAIR mode it persists changes to the container metadata table and can create the chunks directory. It does not directly update the `.container` YAML descriptor. Reports are JSON strings sent to a logger and returned by the overload used in tests/debug tools.

## Dependencies and Integration Points
`ContainerInspectorUtil` registers this inspector for datanode startup inspection. `InspectSubcommand` in the debug CLI constructs it in inspect mode for explicit inspection. `KeyValueContainerUtil` references its pending-delete aggregation logic. It depends on Jackson JSON nodes, Ozone DB table iterators, schema-specific datanode store implementations, deleted-block transactions, and `VersionedDatanodeFeatures`.

## Risks and Test Signals
Repair mode writes DB metadata based on a full scan, so schema selection and prefix filters must be correct. The pending-delete byte repair action currently returns `false` even after a successful `put`, so JSON can report `"repaired": false` despite the write. Schema-v2 pending delete iteration scans the whole delete transaction table, while schema-v3 uses the container prefix. Tests in `TestKeyValueContainerMetadataInspector` cover load modes, inspect vs repair behavior, aggregate mismatch reports, chunk directory repair, and report logging; schema upgrade tests also rely on inspector-compatible aggregate logic.
