<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_format_configs.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/run_format_configs.sh

Purpose: reruns known failing `test/format` configurations from `test/format/failure_configs` in parallel to catch regressions and recover aborted tests.

Important functions: `wait_for_process()` polls PIDs, removes completed PIDs from the list, waits to get exit status, maps PID to config via `format_list.txt`, optionally runs recovery (`./t -Rqv`) when the log contains `aborting to test recovery`, prints prefixed logs, removes successful outputs, and records success/failure counts.

Control flow: moves to repo root then `cmake_build/test/format`, validates `t`, parses `-j`, starts `./t -1 -c <config> -h WT_TEST_<config>` jobs up to `parallel_jobs`, then drains. Exits nonzero if any config failed.

State and persistence: writes `format_list.txt`, per-config logs and WT_TEST directories; removes successful outputs and keeps failed CONFIG/logs for diagnostics.

Dependencies and integration: Evergreen format failure-config task. Requires built `t` and failure config files.

Risks and test signals: polling with `ps` and manual PID arrays is race-prone. The script references `fatal_msg` for invalid `-j` but does not define it. Recovery path copies potentially large directories. Logs are always printed for completed configs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_format_configs.sh -->
