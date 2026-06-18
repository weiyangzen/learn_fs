# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DatanodeSchemaV3FinalizeAction.java

Purpose: finalizes datanode volume layout for Schema V3, where container metadata moves to per-volume RocksDB stores.

Important APIs and functions: annotated for `DATANODE_SCHEMA_V3`. `execute` gets data and DB volume sets, locks the data volume set, creates a DB store for each `HddsVolume` lacking `dbParentDir`, unlocks, then checks `DatanodeConfiguration.getContainerSchemaV3Enabled`. If enabled, it calls `HddsVolumeUtil.loadAllHddsVolumeDbStore`.

Control flow and state: volume DB directory creation occurs regardless of the runtime schema-v3 enabled flag, while DB loading is skipped if the flag is disabled. The write lock protects volume metadata updates during store creation.

Dependencies and integration: used during layout finalization and interacts with `OzoneContainer` startup, which also loads stores when Schema V3 is finalized and enabled.

Risks and test signals: partial DB store creation and lock handling are key. Tests should cover null data volume set rejection, existing DB parent skip, DB volume set null behavior, disabled schema-v3 flag, load failure, and lock release on exceptions.
