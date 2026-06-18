# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/InitialConstraintUpgradeAction.java

Purpose: `InitialConstraintUpgradeAction` is the upgrade action for the initial Recon layout feature. It repairs the `UNHEALTHY_CONTAINERS` table check constraint so it includes all current `UnHealthyContainerStates` enum values.

Important APIs and types: annotated with `@UpgradeActionRecon(feature = INITIAL_VERSION)`. `execute(DataSource)` gets a connection, skips work if the unhealthy container table does not exist, builds a jOOQ DSL context, drops the existing `<table>ck1` constraint, and adds a new constraint over `container_state`.

Control flow and integration: `ReconLayoutFeature.registerUpgradeActions()` discovers the annotation, and `ReconLayoutVersionManager.finalizeLayoutFeatures()` executes it when MLV is below the feature version.

State and persistence: modifies SQL schema constraints in the Recon DB. It does not change data rows.

Dependencies: Recon container schema constants, SQL table existence helper, jOOQ DSL, DataSource, SLF4J.

Risks and test signals: dropping a constraint that does not exist may fail. The action assumes the constraint name convention. Tests should cover table missing, constraint replacement, enum value coverage, and SQL exception wrapping. It exposes a test setter for DSL context.
