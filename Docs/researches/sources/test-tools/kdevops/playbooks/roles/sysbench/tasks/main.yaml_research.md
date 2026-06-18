# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/main.yaml

Purpose: top-level sysbench role dispatcher that prepares directories, dependencies, storage, and selects MySQL Docker or PostgreSQL native execution.

Important APIs/types/functions: optional `include_vars`, `file` directory creation, `include_tasks` for `install-deps`, role `create_data_partition`, and includes for `mysql-docker/main.yaml` and `postgresql-native/main.yaml`.

Control flow: imports extra vars, creates sysbench directories, installs dependencies, optionally creates the data partition, then branches into the selected database backend. A final debug/fail style guard handles unsupported configuration.

State/persistence behavior: creates local/remote directories and delegates package, filesystem, database, telemetry, and result persistence to included tasks.

Dependencies/integration: consumes defaults and Kconfig variables, uses `data_device`, `kdevops_baseline_and_dev`, and backend booleans. Integrates with `create_data_partition`.

Risks/test signals: conflicting backend booleans or missing storage variables can dispatch the wrong backend or skip required setup. Test signals are include selection, created directories, and backend-specific results.
