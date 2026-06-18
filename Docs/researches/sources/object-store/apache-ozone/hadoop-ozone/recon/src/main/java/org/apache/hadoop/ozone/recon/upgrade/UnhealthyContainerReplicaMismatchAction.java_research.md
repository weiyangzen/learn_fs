# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UnhealthyContainerReplicaMismatchAction.java

Purpose: `UnhealthyContainerReplicaMismatchAction` updates the unhealthy container state check constraint when the replica mismatch state is added.

Important APIs and types: annotated for `UNHEALTHY_CONTAINER_REPLICA_MISMATCH`. `execute(DataSource)` checks table existence, creates a DSL context, drops `<UNHEALTHY_CONTAINERS>ck1`, and adds a new check constraint with all enum names from `ContainerSchemaDefinition.UnHealthyContainerStates`.

Control flow and integration: invoked by layout feature finalization after reflection registration.

State and persistence: mutates SQL schema constraints in Recon DB. No data rows are changed.

Dependencies: container schema definition, SQL table existence helper, jOOQ DSL, DataSource.

Risks and test signals: same name assumptions as `InitialConstraintUpgradeAction`; repeated execution or missing constraint can fail. Tests should cover constraint replacement, missing table skip, enum coverage, and exception wrapping.
