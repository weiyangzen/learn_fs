# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/ContainerUpgradeResult.java

Purpose: `ContainerUpgradeResult` records the outcome of upgrading one container from datanode schema V2 to schema V3.

Important APIs and types: It stores original `ContainerData`, optional new `ContainerData`, row count, monotonic start/end times, status, backup `.container` path, and new `.container` path. Methods include setters, getters, `success`, `getCostMs`, `toString`, and enum `Status`.

Control flow: Construction captures the original container and start time. `success` records total migrated rows, end time, and `SUCCESS`. `toString` emits schema versions and file paths when new data is available.

State and persistence behavior: The object is in-memory only, but its file-path fields refer to persisted backup and rewritten container metadata files.

Dependencies and integration points: `UpgradeContainerSchema.UpgradeTask` creates and fills these results while migrating per-container RocksDB rows to the volume DB.

Risks: Failed results never set `endTimeMs`, so `getCostMs` can be negative. The class assumes original/new data are `KeyValueContainerData` when formatting schema versions.

Test signals: Tests should assert success state, row count, timing, string content with and without new data, backup/new path propagation, and failed-result timing behavior.
