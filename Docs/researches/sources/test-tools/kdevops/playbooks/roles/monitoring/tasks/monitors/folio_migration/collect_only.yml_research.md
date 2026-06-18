<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect_only.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect_only.yml

Purpose: interim folio migration collection that copies current stats without stopping the sampler.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.shell`, `ansible.builtin.fetch`, `ansible.builtin.file`, `ansible.builtin.debug`, `ansible.builtin.command`, `ansible.builtin.find`; variables/facts `become_method`, `flat`, `validate_checksum`, `ignore_errors`, `msg`, `patterns`; tasks `Check if folio migration monitoring data exists`, `Create folio migration snapshot for interim collection`, `Copy folio migration interim data to localhost`, `Clean up folio migration snapshot`, `Display folio migration interim collection status`.

Control flow: Stats the live data file, copies it to a snapshot, fetches it to localhost as an interim result, and leaves the monitor running.

State and persistence behavior: Persists a temporary snapshot on target and an interim stats file on localhost.

Dependencies and integration points: Imported by `monitor_collect_only.yml`. Depends on `/root/monitoring/folio_migration_stats.txt`.

Risks: A simple `cp` can race with the writer and capture a partially updated timestamp block. The caller performs cleanup.

Test signals: Signals are existing source stats, fetched interim text, and unchanged sampler PID.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect_only.yml -->
