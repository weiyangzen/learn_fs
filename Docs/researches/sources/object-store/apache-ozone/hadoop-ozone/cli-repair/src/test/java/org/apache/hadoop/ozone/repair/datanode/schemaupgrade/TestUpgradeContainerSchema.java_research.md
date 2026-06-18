## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/TestUpgradeContainerSchema.java

Purpose: integration-heavy tests for datanode container schema-v2 to schema-v3 repair.

Important APIs and control flow: setup creates temporary datanode volume and metadata directories, writes datanode layout storage and ID files, creates v2 containers with block/chunk data, shuts down volumes, and executes `ozone repair datanode upgrade-container-schema` with injected configuration. `failsBeforeOzoneUpgrade` verifies the command rejects runs before the required layout feature. `testUpgrade` runs both dry-run and real modes, checks per-volume/per-container success, verifies backup/new container data files and schema versions, and for real mode reads the schema-three block table to compare migrated block data.

State and dependencies: creates real container files and RocksDB data under JUnit temp dirs. Uses volume sets, block/chunk managers, schema-three store, and codec leak detection.

Risks and test signals: strong coverage for happy path, dry-run behavior, layout gate, backup files, and data preservation. Failure modes such as partial volume upgrade or lock contention are less visible here.
