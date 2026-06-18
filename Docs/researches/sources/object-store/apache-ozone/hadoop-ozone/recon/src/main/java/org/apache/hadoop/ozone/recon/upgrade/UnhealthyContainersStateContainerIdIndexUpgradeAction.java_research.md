# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainersStateContainerIdIndexUpgradeAction.java

Purpose: this upgrade action ensures the `idx_state_container_id` index exists on `UNHEALTHY_CONTAINERS` for efficient state and container id lookups after the related layout feature.

Important APIs and types: annotated for `UNHEALTHY_CONTAINERS_STATE_CONTAINER_ID_INDEX`. `execute(DataSource)` checks table existence, checks index existence through `DatabaseMetaData.getIndexInfo`, and creates the index on `container_state` and `container_id` with jOOQ if absent.

Control flow and integration: discovered and run by the layout manager for feature version 5.

State and persistence: creates a SQL index in the Recon DB. It is idempotent if metadata lookup finds the index.

Dependencies: JDBC `DatabaseMetaData`, jOOQ DSL, container schema constants, table existence helper.

Risks and test signals: index lookup depends on DB metadata casing and table name matching. Tests should cover missing table, existing index case-insensitively, index creation, SQL exception wrapping, and query plans or repository methods that rely on the new index.
