# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdaterManager.java

Purpose: `ReconTaskStatusUpdaterManager` is a singleton cache and lazy loader for `ReconTaskStatusUpdater` instances. It avoids reading task status rows during Guice injection, which matters during schema upgrades.

Important APIs and types: constructor receives `ReconTaskStatusDao` and initializes a `ConcurrentHashMap`. `getTaskStatusUpdater(taskName)` calls `ensureInitialized()` and then `computeIfAbsent`. `ensureInitialized()` double-checks an `AtomicBoolean`, uses jOOQ DSL to inspect schema, loads either full rows or base columns, and populates the cache. `columnExists` checks Derby system catalogs for upgrade columns.

Control flow and integration: the controller requests updaters during task lifecycle. Before the `TASK_STATUS_STATISTICS` upgrade is finalized, the manager can query only old columns and defaults new fields to zero.

State and persistence: cache state is in memory. Persistent data lives in `RECON_TASK_STATUS`.

Dependencies: Guice singleton, jOOQ DAO/DSL, generated `ReconTaskStatus`, Derby system catalog naming.

Risks and test signals: `initialized` is only set on successful load, so transient DB errors retry on later access. Column detection is Derby-specific. Tests should cover pre-upgrade schema, upgraded schema, retry after load failure, concurrent first access, and creation of new updater rows.
