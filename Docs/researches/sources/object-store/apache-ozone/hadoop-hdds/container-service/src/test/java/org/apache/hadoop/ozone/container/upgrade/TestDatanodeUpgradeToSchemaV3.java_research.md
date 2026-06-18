## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToSchemaV3.java

Purpose: Broad upgrade suite for transitioning datanode container schema V2 to schema V3 and DB-volume handling, parameterized with schema V3 enabled and disabled.

Important APIs/types/functions: `DatanodeStateMachine.finalizeUpgrade`, `VersionedDatanodeFeatures.SchemaV3.isFinalizedAndEnabled`, `DatanodeConfiguration.CONTAINER_SCHEMA_V3_ENABLED`, `HDDSLayoutFeature.DATANODE_SCHEMA_V3`, `HddsVolume`, `DbVolume`, `DatanodeLayoutStorage`, and `UpgradeTestHelper`.

Control flow: Tests DB creation on data volumes and configured DB volumes, creation during finalize for existing formatted volumes, idempotent double finalize, adding HDDS/DB volumes after finalize, schema choice for new writes after restart, reads during concurrent finalization, and finalize failure rollback/readability. `testWrite` first writes schema V2 data with V3 disabled, restarts after finalization with a selected flag, writes another container, and asserts expected schema. Failure test mocks DB creation failure, catches finalize exception, then verifies old V2 data remains readable before and after restart.

State and persistence behavior: Creates real layout storage, volume directories, DB parent directories, container data, and SCM endpoint state. Mutates config between restarts to model cluster rollout.

Dependencies and integration points: Integrates datanode layout manager, volume sets, DB volumes, container dispatcher, datastream config, SCM RPC, and schema feature gates.

Risks and test signals: High-value upgrade and data-safety coverage. Many tests are integration-heavy and can be sensitive to filesystem timing, restart semantics, and feature-flag interpretation.
