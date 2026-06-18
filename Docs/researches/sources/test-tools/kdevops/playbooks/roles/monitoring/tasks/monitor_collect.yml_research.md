<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect.yml

Purpose: final collection path for monitoring data; it stops active monitors, generates target-side or localhost visualizations, fetches artifacts, and invokes comparison scripts.

Important APIs/types/functions: modules `ansible.builtin.set_fact`, `ansible.builtin.stat`, `ansible.builtin.shell`, `ansible.builtin.debug`, `ansible.builtin.find`, `ansible.builtin.file`, `ansible.builtin.fetch`, `ansible.builtin.command`; variables/facts `monitoring_results_path`, `become_method`, `msg`, `ignore_errors`, `patterns`, `file_type`, `flat`, `validate_checksum`, `cmd`, `monitoring_results_dir`; tasks `Set monitoring results path`, `Check if fragmentation monitoring was started`, `Stop fragmentation monitoring`, `Display stop fragmentation monitoring status`, `Generate fragmentation visualization`.

Control flow: Imports common setup and folio collect tasks, computes a workflow-specific results path, SIGINTs fragmentation tracker, records end time, optionally runs `fragmentation_visualizer.py`, finds output files, fetches them to localhost, generates fragmentation comparisons, and includes `visualize.yml`.

State and persistence behavior: Persists fetched files under `<workflow>/results/monitoring`, plus comparison PNGs. Removes the target PID file after shutdown and writes end time on target.

Dependencies and integration points: Invoked after monitored workflows. Integrates tracker/snapshot data, folio migration data, and the scripts under `roles/monitoring/scripts`.

Risks: It resets `monitoring_results_path` once to an fstests default after a richer workflow path calculation, which can misplace outputs unless `monitoring_results_base_path` is set. The stop loop waits indefinitely.

Test signals: Test with folio-only, fragmentation-only, and both monitors; verify fetched artifacts, generated comparisons, and graceful no-data behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect.yml -->
