# sources/storage-engines/wiredtiger/test/format/format.sh

## Purpose
`format.sh` is the shell harness for repeatedly running the compiled format binary. It supports smoke tests, randomized stress options, abort/recovery testing, directories of configs, parallel jobs, optional live recording, timeout handling, failure categorization, and cleanup of successful run directories.

## Important APIs, Types, And Functions
The script defines `usage`, `msg`, `fatal_msg`, `verbose`, `force_quit_reason`, `shuffle`, `skip_known_errors`, `categorize_failure`, `report_failure`, `report_running_configs`, `wait_for_process`, `resolve`, `format`, and `check_timer`. It uses `nohup setsid`, `/proc`, `pstree`, `kill`, `grep`, `sed`, `awk`, and optional recording tools.

## Control Flow
After parsing options, the script resolves absolute paths for home and config, changes to the build directory, validates the format and `wt` binaries, and enters a scheduler loop. The loop starts jobs until the parallel limit or total/smoke/config-directory limits are reached, periodically calls `resolve`, handles elapsed-time limits, and exits when no work remains or a force-quit condition drains running jobs.

## State And Persistence Behavior
Each job writes `RUNDIR.N.log` and usually `RUNDIR.N/CONFIG`. Successful jobs are removed. Failed jobs are retained and marked with `format.sh-status`. Abort/recovery jobs copy the directory to `.RECOVER`, rerun recovery, and remove artifacts on success. Out-of-space conditions trigger reporting of still-running configurations.

## Dependencies And Integration Points
The harness assumes a WiredTiger build tree with `./t`, `../../wt`, and config files. It passes `quiet=1` to jobs, can inject trace flags, abort mode, split stress flags, environment variables, and user config overrides. It is independent from the C runtime but drives the main stress-test execution pattern.

## Risks And Test Signals
Risks include shell quoting around `format_binary`, stale log PID parsing, process-group kill behavior, disk exhaustion, and unknown exits being classified as script problems. Signals include counts of successful/failed jobs, retained failed directories, categorized config excerpts, abort/recovery rerun logs, and explicit out-of-space reports.
