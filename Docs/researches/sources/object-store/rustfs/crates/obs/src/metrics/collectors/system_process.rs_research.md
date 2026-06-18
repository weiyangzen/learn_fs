# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_process.rs

Purpose: emits detailed RustFS process metrics and provides process attribute collection for labels.

Important APIs/types: `ProcessAttributes`, `ProcessAttributeError`, `ProcessStatusType`, `ProcessStats`, `collect_process_metrics`, and `collect_process_attributes`. `ProcessAttributes::current` and `from_pid` query sysinfo for PID/name/path/cmd. `ProcessStatusType` normalizes `sysinfo::ProcessStatus`.

Control flow: `collect_process_metrics` creates seventeen descriptor-backed process metrics plus a status metric labeled with the debug string of `ProcessStatusType`. `from_pid` refreshes only the requested process, errors when unavailable, and joins command args into a string. `to_labels` returns four labels: PID, executable name, executable path, and command.

State/persistence: no persistent state, but it queries live process metadata via sysinfo. Scheduler uses a smaller label set through `current_process_metric_labels`, currently PID and executable name, with fallback on error.

Dependencies/integration: system monitoring scheduler emits full process metrics at the resource interval and uses process attributes for process CPU/memory/disk/GPU labels.

Risks: full `process_command` and executable path can be high-cardinality or sensitive if used as labels; scheduler avoids them in its current helper. Status metric uses a numeric value plus string label, so value/label conventions must stay stable.

Test signals: tests assert eighteen metrics, representative uptime/file descriptor/status values, default metric count, current process attribute collection, status conversion, and label formatting.
