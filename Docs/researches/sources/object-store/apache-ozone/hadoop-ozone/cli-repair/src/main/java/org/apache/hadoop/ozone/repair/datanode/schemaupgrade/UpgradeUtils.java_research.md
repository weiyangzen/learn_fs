## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/UpgradeUtils.java

Purpose: package-private utility support for datanode schema-v2 to schema-v3 container upgrade repair. It centralizes volume discovery, datanode identity loading, layout-version inspection, marker-file naming, and column-family enumeration used by the actual upgrade tool.

Important APIs and control flow: `COLUMN_FAMILY_NAMES` is derived from `DatanodeSchemaTwoDBDefinition` so migration copies the schema-v2 table set consistently. `getDatanodeDetails` reads the configured datanode ID file and fails early if missing. `getLayoutFeature` opens `DatanodeLayoutStorage`, builds an `HDDSLayoutVersionManager`, and returns software and metadata features as a pair. `getAllVolume` builds a `MutableVolumeSet` and filters to `HddsVolume` instances. `createFile` writes a timestamp to marker files.

State and dependencies: persistent state is filesystem-based: `upgrade.complete`, `upgrade.lock`, and backup suffix conventions in each HDDS volume root. Dependencies are Ozone configuration, datanode layout storage, volume utilities, and schema DB definitions.

Risks and test signals: marker-file creation is simple but not atomic beyond the single file write, so concurrent manual runs rely on higher-level locking. Tests in `TestUpgradeContainerSchema` indirectly exercise ID, volume, layout, and marker behavior during end-to-end upgrade.
