# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutVersionManager.java

Purpose: `ReconLayoutVersionManager` determines Recon's metadata layout version, compares it with software layout version, and finalizes pending layout features during startup.

Important APIs and types: constructor receives `ReconSchemaVersionTableManager`, `ReconContext`, and `DataSource`, reads current MLV, and registers upgrade actions. `finalizeLayoutFeatures()` finds features with version greater than MLV, opens a transaction, updates schema version, executes feature action if present, commits per feature, and rolls back on failure. `getRegisteredFeatures`, `getCurrentMLV`, and `getCurrentSLV` expose state.

Control flow and integration: startup code creates this manager and calls finalization. On failure, it updates Recon context errors with `UPGRADE_FAILURE`, marks health false, and throws a runtime exception to halt startup.

State and persistence: `currentMLV` is cached in memory and persisted through `ReconSchemaVersionTableManager.updateSchemaVersion`. Upgrade actions mutate schema or trigger rebuilds.

Dependencies: SQL connection and data source, Recon context, schema version manager, `ReconLayoutFeature`.

Risks and test signals: schema version is updated before action execution within the transaction connection, but actions receive `DataSource` and may use separate connections, which can weaken transaction assumptions. Features without actions are logged but their versions are not advanced because update occurs only inside `action.isPresent()`. Tests should cover feature ordering, rollback behavior, context health update, no-action version behavior, and action failures.
