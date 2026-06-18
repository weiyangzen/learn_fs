# sources/test-tools/kdevops/playbooks/roles/sysbench/defaults/main.yml

Purpose: default variable set for the sysbench role, covering MySQL Docker mode, PostgreSQL native mode, filesystem formatting, benchmark sizing, telemetry paths, and durability toggles.

Important APIs/types/functions: exports Ansible defaults such as `sysbench_type_mysql_docker`, `sysbench_type_postgresql_native`, `sysbench_device`, `sysbench_fstype`, `sysbench_oltp_table_size`, `sysbench_threads`, container names/images, PostgreSQL source/PGDATA paths, and full-page-write/doublewrite controls.

Control flow: no executable flow; these defaults are consumed by `tasks/main.yaml`, database-specific task files, filesystem creation roles, templates, and plotting commands.

State/persistence behavior: defaults point persistent state at `/db`, `/data`, PostgreSQL source under `data_path`, telemetry under `/data/sysbench-telemetry`, and controller results under workflow paths created by task files.

Dependencies/integration: integrates Kconfig-generated overrides, inventory host naming for baseline/dev comparisons, Docker, MySQL, PostgreSQL, sysbench, and kdevops data partition roles.

Risks/test signals: unsafe defaults like `sysbench_device: /dev/null` prevent accidental device writes but must be overridden for real tests. Test signals are effective variable dumps in task output, generated database config files, and expected telemetry/result files.
