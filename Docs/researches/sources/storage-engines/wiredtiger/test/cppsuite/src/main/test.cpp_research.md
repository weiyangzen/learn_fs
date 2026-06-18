# sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.cpp

## Purpose
Implements the base cppsuite test lifecycle: parse configuration, construct framework components, open the WiredTiger connection, start components, wait for population, run for the configured duration, stop, validate, and emit performance metrics.

## Important APIs, Types, And Functions
`test::test` wires `configuration`, `timestamp_manager`, `workload_manager`, `thread_manager`, optional `metrics_monitor`, database timestamp/config settings, and component list membership. `init_operation_tracker` creates or installs the operation tracker. `run` performs the complete test lifecycle. The destructor releases owned components.

## Control Flow
Construction prepares components but does not run them. `run` builds the `wiredtiger_open` config from compression, reverse collator, cache size, statistics, logging, background compact debug, cache wait, in-memory mode, file sweep interval, and user config. It removes the home directory, creates the connection, loads all components, starts each component on `thread_manager`, polls until `workload_manager::db_populated()`, sleeps for `DURATION_SECONDS`, calls `end_run`, joins component threads, calls `finish`, optionally validates, writes perf stats, and logs `SUCCESS`.

## State And Persistence Behavior
The class owns heap-allocated framework components and a `database` model. It recreates the test home directory before opening WiredTiger, so previous artifacts are removed. It configures collection creation behavior for compression and reverse collator. Validation uses the operation tracker table names and the workload manager database model.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `metrics_writer`, `configuration`, `timestamp_manager`, `workload_manager`, `metrics_monitor`, `operation_tracker`, `thread_manager`, and `connection_manager`. Concrete test classes usually only define a constructor and override selected `database_operation` hooks.

## Risks And Test Signals
Raw pointers require the destructor to stay aligned with constructor/init paths. `init_operation_tracker` must be called by concrete tests before `run`, otherwise `_operation_tracker` is null when validation or workload tracking is expected. Connection configuration strings are assembled manually and may be sensitive to malformed user `wt_open_config`. Test success is signaled by component completion, optional validation passing, perf file output, and final `SUCCESS` log.
