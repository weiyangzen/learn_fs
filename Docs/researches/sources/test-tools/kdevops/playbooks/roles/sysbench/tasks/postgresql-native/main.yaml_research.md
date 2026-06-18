# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/postgresql-native/main.yaml

Purpose: end-to-end native PostgreSQL sysbench workflow that builds PostgreSQL from source, formats a target device, initializes a database cluster, runs OLTP workload, gathers telemetry, and plots results.

Important APIs/types/functions: uses shell/git to resolve PostgreSQL ref, `ansible.builtin.git`, `nproc`, `community.general.make`, `user`, `stat`, `pg_ctl`, `initdb`, `psql`, role `create_partition`, PostgreSQL config template, sysbench command-line driver, `pg_controldata`, `fetch`, `journalctl`, debugfs extfrag files, and local sysbench plotting scripts.

Control flow: selects baseline/dev device, resolves and clones PostgreSQL, configures/builds/installs with requested block sizes, ensures PostgreSQL user and telemetry directory, stops existing server, derives filesystem options, wipes and recreates target filesystem, initializes PGDATA, toggles `full_page_writes`, renders config, records kernel/settings, starts PostgreSQL, creates user/database/grants, verifies write permission, populates with sysbench, runs benchmark, escalates PostgreSQL stop from smart to fast/immediate if needed, writes run and control data logs, gathers telemetry and kernel/memory signals, optionally cleans results, and generates plots.

State/persistence behavior: installs PostgreSQL under `/usr/local/pgsql`, creates or replaces `sysbench_mnt` data, writes PGDATA and logs, creates database users/databases, produces telemetry under `/data/sysbench-telemetry`, and copies outputs to controller result paths.

Dependencies/integration: depends on PostgreSQL build deps, sysbench PostgreSQL driver, generated filesystem variables, `create_partition`, `sysbench_postgresql_*` defaults, and A/B host naming conventions.

Risks/test signals: destructive device formatting, source build nondeterminism, changed_when expressions that compare result objects incorrectly, SQL grant mistakes, and stop escalation are key risks. Test signals are build/install success, `pg_ctl` start, permission test, populated tables, sysbench output, `pg_controldata`, copied telemetry, and plots.
