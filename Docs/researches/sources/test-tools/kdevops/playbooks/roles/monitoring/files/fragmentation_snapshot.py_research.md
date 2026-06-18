<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_snapshot.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_snapshot.py

Purpose: creates an interim memory-fragmentation snapshot without losing ongoing monitoring continuity. It stops the running tracker with SIGINT so the tracker writes a valid JSON file, copies the latest `fragmentation_data*.json` to `fragmentation_snapshot.json`, then starts a fresh tracker instance in `/opt/fragmentation`.

Important APIs/types/functions: `get_pid_from_file()`, `is_process_running()`, `stop_tracker_and_save()`, `find_latest_json()`, `start_new_tracker()`, `create_snapshot()`, `main()`.

Control flow: `main()` validates the output directory argument, `create_snapshot()` reads `fragmentation_tracker.pid`, verifies the process with `os.kill(pid, 0)`, calls `stop_tracker_and_save()`, finds the newest data JSON, writes the snapshot, and launches `fragmentation_tracker.py -o fragmentation_data_<timestamp>.json` with stdout/stderr appended to the tracker log.

State and persistence behavior: Persists `fragmentation_snapshot.json`, a new timestamped data file, `fragmentation_tracker.log`, and an updated `fragmentation_tracker.pid` in the configured output directory. It intentionally copies rather than renames the last complete tracker output.

Dependencies and integration points: Called by `monitor_collect_only.yml` on target hosts. Depends on Python 3, process signals, `/opt/fragmentation/fragmentation_tracker.py`, and root-accessible monitoring output paths.

Risks: The wait for tracker exit is unbounded, stale PID reuse is only checked by signalability, and `find_latest_json()` may select an older complete file if the tracker fails before writing. Starting a new process has no post-start health check.

Test signals: Useful signals are `no_pid_file`, `not_running`, `no_json_found`, creation of valid JSON, PID rollover, and continued tracker logging after snapshot.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_snapshot.py -->
