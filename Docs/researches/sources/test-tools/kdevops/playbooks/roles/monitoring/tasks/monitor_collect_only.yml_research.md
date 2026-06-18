<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect_only.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect_only.yml

Purpose: interim collection path that snapshots monitoring data while keeping monitoring active.

Important APIs/types/functions: modules `ansible.builtin.shell`, `ansible.builtin.copy`, `ansible.builtin.command`, `ansible.builtin.debug`, `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.stat`, `ansible.builtin.fetch`; variables/facts `become_method`, `cmd`, `msg`, `args`, `chdir`, `monitor_developmental_stats`, `monitor_folio_migration`, `enable_monitoring`, `monitoring_results_path`, `flat`; tasks `Check if fragmentation tracker is running`, `Copy fragmentation snapshot script to target`, `Create fragmentation data snapshot`, `Display fragmentation snapshot status`, `Create snapshot of monitoring data`.

Control flow: Imports setup and folio collect-only tasks, checks tracker status, copies/runs `fragmentation_snapshot.py`, fetches folio and fragmentation snapshots, optionally generates local folio plots, then removes snapshot files from targets.

State and persistence behavior: Persists interim files named `*_interim.txt` and `*_interim.json` on localhost while retaining the long-running monitor. Target snapshot files are cleaned up.

Dependencies and integration points: Used during long workflows to inspect progress. Depends on active PID files, `/root/monitoring`, matplotlib on localhost for plots, and the snapshot helper.

Risks: The folio snapshot task references `folio_migration_data_file` from an imported file; if import is skipped, conditions must remain safe. Plot summary messages are inconsistent and a variable named `folio_interim_plot_generation` is referenced but not set in this file.

Test signals: Signals are continued tracker PID after collection, valid interim JSON/text, generated plots when matplotlib exists, and cleanup of target snapshot files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect_only.yml -->
