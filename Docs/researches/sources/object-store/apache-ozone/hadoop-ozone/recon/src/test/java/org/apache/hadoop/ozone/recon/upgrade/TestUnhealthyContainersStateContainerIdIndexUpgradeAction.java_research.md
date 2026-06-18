# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestUnhealthyContainersStateContainerIdIndexUpgradeAction.java

Purpose: Tests `UnhealthyContainersStateContainerIdIndexUpgradeAction`, which creates an index named `idx_state_container_id` on the unhealthy containers table.

Important APIs and control flow: Setup obtains real test `DSLContext` and `DataSource`. Tests create the table without the index, execute the upgrade, verify index existence via JDBC metadata, rerun execute to prove idempotence, and drop the table to prove missing-table no-op behavior.

State and persistence behavior: Mutates test SQL schema by creating/dropping `UNHEALTHY_CONTAINERS` and inspecting metadata indexes. The persistent contract is that the state/container-id index exists when the table exists and repeated upgrade execution is safe.

Dependencies and integration points: Uses `ContainerSchemaDefinition.UNHEALTHY_CONTAINERS_TABLE_NAME`, `SqlDbUtils.TABLE_EXISTS_CHECK`, jOOQ, and JDBC metadata. This supports query performance and upgrade compatibility for Recon unhealthy container APIs.

Risks and test signals: Good signal for idempotent schema migration. Risk is database-specific metadata casing or index reporting, mitigated by case-insensitive comparison.
