# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconTaskStatusTableUpgradeAction.java

Purpose: `ReconTaskStatusTableUpgradeAction` adds task status tracking columns to `RECON_TASK_STATUS` for the task status statistics feature.

Important APIs and types: annotated for `TASK_STATUS_STATISTICS`. `execute(DataSource)` skips missing tables, adds nullable integer columns `last_task_run_status` and `is_current_task_running`, updates existing rows to zero, then sets both columns not null. Helpers perform add-column and set-not-null operations with jOOQ.

Control flow and integration: discovered by `ReconLayoutFeature` and run by `ReconLayoutVersionManager`. `ReconTaskStatusUpdaterManager` has compatibility logic to read old rows before this action runs.

State and persistence: changes SQL schema and initializes column values on existing rows.

Dependencies: generated schema constants, table existence helper, jOOQ DSL and SQL types, Recon task schema definition.

Risks and test signals: the catch block logs `SQLException` or `DataAccessException` but does not rethrow, which may let layout finalization commit despite failed schema migration. Existing columns are not checked, so reruns can fail. Tests should cover missing table, happy path, row defaults, not-null constraints, existing-column behavior, and exception propagation expectations.
