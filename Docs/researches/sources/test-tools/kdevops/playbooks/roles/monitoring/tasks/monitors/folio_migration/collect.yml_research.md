<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect.yml

Purpose: final folio migration collection task. It stops the sampler, plots data, fetches stats and images, and summarizes results.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.shell`, `ansible.builtin.debug`, `ansible.builtin.copy`, `ansible.builtin.command`, `ansible.builtin.fetch`; variables/facts `become_method`, `msg`, `ignore_errors`, `args`, `chdir`, `flat`, `validate_checksum`; tasks `Check if folio migration monitoring was started`, `Stop folio migration monitoring`, `Display stop monitoring status`, `Check if monitoring data was collected`, `Copy plot_migration_stats.py to target`.

Control flow: Checks the PID file, kills the monitor process, verifies `folio_migration_stats.txt`, copies plot script, checks matplotlib, runs target-side plotting, creates local result directories, fetches stats and plots, then reports collected files.

State and persistence behavior: Persists target stop state and local copied stats/plots under monitoring results.

Dependencies and integration points: Imported by `monitor_collect.yml`. Depends on `/root/monitoring`, plot script, matplotlib availability, and the sampler PID.

Risks: Killing without robust process-group cleanup can miss child shell loops. Target-side plotting requires matplotlib on targets even though other paths plot on localhost.

Test signals: Signals include stopped PID, fetched stats, generated PNG when matplotlib exists, and no failure when data is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect.yml -->
