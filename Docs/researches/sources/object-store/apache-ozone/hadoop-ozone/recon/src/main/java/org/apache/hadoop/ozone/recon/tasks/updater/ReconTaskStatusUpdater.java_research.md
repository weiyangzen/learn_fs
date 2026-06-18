# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/updater/ReconTaskStatusUpdater.java

Purpose: `ReconTaskStatusUpdater` is a small mutable facade over the generated jOOQ `ReconTaskStatusDao` and POJO. It records task run starts, completions, sequence numbers, and status flags in the `RECON_TASK_STATUS` table.

Important APIs and types: constructors create an updater from a DAO and task name or from an existing `ReconTaskStatus` row. Setters update task name, last sequence, timestamp, last run status, and current-running flag. `recordRunStart()` sets running true and timestamp, then writes. `recordRunCompletion()` sets running false and timestamp, then writes. `updateDetails()` inserts if missing or updates if present.

Control flow and integration: `ReconTaskControllerImpl` obtains updaters from `ReconTaskStatusUpdaterManager` before and after delta and reprocess execution. Upgrade-aware manager construction avoids schema access before columns exist.

State and persistence: holds a mutable POJO snapshot and writes it to the SQL Recon task status table.

Dependencies: generated jOOQ DAO/POJO, `DataAccessException`, SLF4J.

Risks and test signals: errors in start/completion logging are swallowed after logging, so task execution may continue with stale status. `updateDetails()` has insert/update race potential if multiple updaters for same name exist. Tests should cover insert, update, run start/completion fields, sequence update, and DAO exception handling.
