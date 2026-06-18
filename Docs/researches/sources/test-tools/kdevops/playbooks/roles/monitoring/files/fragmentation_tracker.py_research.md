<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_tracker.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_tracker.py

Purpose: runs the eBPF side of memory fragmentation monitoring, centered on the `kmem:mm_page_alloc_extfrag` tracepoint with optional compaction tracepoints. It converts kernel perf events into JSON event records and summary statistics for later visualization.

Important APIs/types/functions: class `FragmentationTracker` with methods `__init__`, `process_event`, `print_summary`, `save_data`, `run`, `main()`.

Control flow: `main()` enforces root, parses `--output`, `--time`, and `--quiet`, installs a SIGINT handler, and starts `FragmentationTracker.run()`. `run()` conditionally enables compaction tracepoint probes, compiles the BCC program, opens the perf buffer, polls until interrupted or timed out, then always prints and saves data. `process_event()` maps raw BPF structs into extfrag, compaction success, or compaction failure dictionaries.

State and persistence behavior: Keeps in-memory `events_data`, per-order extfrag counts, and per-order compaction success/failure counts. On exit it writes metadata, events, and statistics JSON including start/end time, duration, total events, and kernel release.

Dependencies and integration points: Depends on BCC Python bindings, kernel tracepoints, debugfs tracing paths, root privileges, and the monitoring Ansible role that copies it to `/opt/fragmentation` and controls its lifetime.

Risks: Tracepoint field names can vary by kernel, node/zone data for extfrag is placeholder `-1`, SIGTERM from `timeout` may not use the graceful save path, and long runs can retain all events in memory. Compaction support depends on tracepoints existing under debugfs.

Test signals: Test by running as root against a kernel with `mm_page_alloc_extfrag`, checking quiet/timed modes, SIGINT save behavior, parseable JSON schema, nonzero stats under allocation pressure, and graceful behavior when compaction tracepoints are absent.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_tracker.py -->
