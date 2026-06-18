# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestInitialConstraintUpgradeAction.java

Purpose: Tests `InitialConstraintUpgradeAction`, specifically schema constraints on the Recon unhealthy containers table.

Important APIs and control flow: Setup obtains a real test `DSLContext`/`DataSource`, creates `InitialConstraintUpgradeAction`, and ensures `UNHEALTHY_CONTAINERS` exists with an initial primary key. The main test executes the upgrade, inserts one row for every `UnHealthyContainerStates` enum value, verifies count, and asserts invalid state insertion fails. Additional tests assert NULL `container_state` and duplicate `(container_id, container_state)` primary key insertions fail.

State and persistence behavior: Mutates an in-memory/test SQL schema through jOOQ. The persistent contract is a table with non-null state, constrained state values, and composite primary key behavior.

Dependencies and integration points: Uses `ContainerSchemaDefinition`, jOOQ DSL, `ReconStorageContainerManagerFacade` data-source access, and `AbstractReconSqlDBTest`. This protects upgrade-time compatibility for Recon SCM unhealthy container state storage.

Risks and test signals: Strong signal for constraint correctness. Risks include test-generated table shape diverging from production migrations and use of `System.currentTimeMillis` as container ID, which is practically unique but not semantically tied to real container IDs.
