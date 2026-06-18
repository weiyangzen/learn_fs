## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToContainerIdsTable.java

Purpose: Tests upgrade from HBase support layout to witnessed container DB proto table schema for container create info.

Important APIs/types/functions: `DatanodeStateMachine.finalizeUpgrade`, `ContainerTableSchemaFinalizeAction`, `WitnessedContainerMetadataStore`, `WitnessedContainerDBDefinition.CONTAINER_CREATE_INFO_TABLE_DEF`, `ContainerCreateInfo`, `ContainerID`, `StringCodec`, and `UpgradeTestHelper`.

Control flow: Starts SCM RPC and a pre-finalized datanode at `HBASE_SUPPORT`, creates a container, verifies old table name `containerIds` stores state as a string, closes the container, finalizes, and verifies the new proto table is selected and contains `ContainerCreateInfo` with state `OPEN`. Retry test manually executes finalize action with extra dummy rows, removes dummy old-table rows, then finalizes and verifies the new table count is reconciled to one.

State and persistence behavior: Uses real metadata DB tables and temporary datanode storage. Table migration state persists across finalize action calls.

Dependencies and integration points: Exercises upgrade finalization, container dispatcher commands, SCM endpoint setup, and witnessed container metadata store.

Risks and test signals: Strong migration idempotency signal. Tests depend on old table name/string codec details and close containers before finalize to satisfy upgrade preconditions.
