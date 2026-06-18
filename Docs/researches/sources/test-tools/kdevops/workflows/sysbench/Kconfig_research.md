<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Kconfig -->
# sources/test-tools/kdevops/workflows/sysbench/Kconfig

## Purpose
This Kconfig file configures sysbench database workload testing in kdevops. It selects Docker/MySQL or native/PostgreSQL modes, imports filesystem and mode-specific config, and defines common workload parameters.

## Important Symbols
Hidden type flags `SYSBENCH_DB_TYPE_MYSQL` and `SYSBENCH_DB_TYPE_POSTGRESQL` feed `SYSBENCH_DB_TYPE`. The main choice defaults to `SYSBENCH_DOCKER`, selecting `SYSBENCH_TYPE_MYSQL_DOCKER`; `SYSBENCH_NATIVE` selects `SYSBENCH_TYPE_POSTGRESQL_NATIVE`. It sources `Kconfig.fs`, `Kconfig.docker`, and `Kconfig.native` conditionally. Common values include database name/user/passwords, report interval, OLTP table size/count, thread selection, test duration, and telemetry path. MySQL-specific tunables include table engine, redo log capacity, and buffer pool size.

## Control Flow and Integration
Selected Kconfig values are emitted to YAML and consumed by `playbooks/sysbench.yml`. Conditional source files expand the configuration surface depending on Docker/native mode and filesystem choices.

## State, Persistence, and Dependencies
Persistent configuration is generated into kdevops vars. Runtime state includes database data, telemetry under `/data/sysbench-telemetry` by default, logs, and plotted results. Dependencies include sysbench, Docker/MySQL or native PostgreSQL, filesystem setup, and monitoring roles.

## Risks and Test Signals
Defaults are example-oriented and may under-size or over-size database buffers for real hardware. Passwords default to `kdevops`, so exposure matters. `SYSBENCH_THREADS` uses duplicate symbol names in mutually exclusive blocks, which is legal but must remain scoped correctly. Test signals are populated tables, sysbench run results, telemetry, and plots.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Kconfig -->
