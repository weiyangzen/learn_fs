<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_run.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_run.yml

Purpose: starts enabled monitoring collectors on target hosts, including folio migration and memory fragmentation tracking.

Important APIs/types/functions: modules `ansible.builtin.file`, `ansible.builtin.copy`, `ansible.builtin.shell`, `ansible.builtin.set_fact`, `ansible.builtin.debug`; variables/facts `become_method`, `async`, `poll`, `fragmentation_monitor_job`, `msg`; tasks `Create fragmentation scripts directory`, `Copy fragmentation monitoring scripts to target`, `Create fragmentation monitoring output directory`, `Start fragmentation monitoring in background`, `Save fragmentation monitor async job ID`.

Control flow: Imports folio migration run tasks, creates `/opt/fragmentation`, copies tracker and visualizer scripts, creates the output directory, starts `fragmentation_tracker.py` with optional `timeout`, saves the PID and start time, and verifies the process exists.

State and persistence behavior: Persists scripts under `/opt/fragmentation`, output/log/PID/start-time files under `monitor_fragmentation_output_dir`, and an async job id fact.

Dependencies and integration points: Consumed before long-running workflows. Depends on root, Python/BCC dependencies, and monitor variables such as `monitor_memory_fragmentation` and `monitor_fragmentation_duration`.

Risks: The `timeout` command can terminate with SIGTERM and may bypass JSON save if not handled. PID verification is immediate and may pass before later BCC compile failures surface in the log.

Test signals: Signals include running PID, populated log, `start_time.txt`, valid JSON after shutdown, and no orphaned process after collection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_run.yml -->
