<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/run.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/run.yml

Purpose: starts folio migration stats sampling on target hosts.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.file`, `ansible.builtin.shell`, `ansible.builtin.set_fact`, `ansible.builtin.debug`; variables/facts `become_method`, `async`, `poll`, `folio_migration_monitor_job`, `msg`; tasks `Check if folio migration stats are available`, `Create monitoring directory`, `Start folio migration monitoring in background`, `Save async job ID for later termination`, `Verify monitoring started successfully`.

Control flow: Creates `/root/monitoring`, initializes stats files, and backgrounds a shell loop that periodically timestamps and reads debugfs migrate_folio stats into `folio_migration_stats.txt`, recording a PID.

State and persistence behavior: Persists `/root/monitoring/folio_migration.pid`, stats text, logs, and start metadata on targets.

Dependencies and integration points: Imported by `monitor_run.yml` when developmental folio monitoring is enabled. Depends on debugfs migration stats support, root, and interval variables.

Risks: Debugfs paths may not exist on kernels without the experimental stats patch; background shell loops can be orphaned if PID handling fails.

Test signals: Test by confirming PID, increasing stats file over time, readable migrate_folio counters, and clean shutdown by collect tasks.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/run.yml -->
