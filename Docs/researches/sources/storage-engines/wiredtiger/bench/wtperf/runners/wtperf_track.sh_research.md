# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_track.sh

## Purpose
`wtperf_track.sh` records Jenkins wtperf metrics over time and emits warnings when short-term or mid-term trends regress against longer baselines.

## Important APIs, Types, and Functions
Functions include `Usage`, `GetValues`, `MinValues`, `AvgValues`, `CheckValues`, `GetCpuLoadAverage`, and `GetDiskLoadAverage`. Required Jenkins environment variables are `JENKINS_HOME`, `JOB_NAME`, and `BUILD_ID`. Options select time (`-t`, lower better), count (`-c`, higher better), and percent threshold (`-p`).

## Control Flow
The script validates environment and arguments, appends a row to `${STATE_DIR}/${JOB_NAME}.${NAME}.csv`, computes `v3` as best of last 3, `v20` as average best 10 of last 20, and `v100` as average best 50 of last 100. It prints current/baseline values and calls `CheckValues` for short and long trends. Warning output is intended for Jenkins to mark instability; final nonzero exit is disabled.

## State and Persistence Behavior
Persistent state lives in `/home/jenkins/wtperf_track/*.csv`, with columns build id, timestamp, value, load average, and disk average. The file grows indefinitely unless managed externally.

## Dependencies and Integration Points
It depends on Jenkins variables, bash/sh utilities, `bc`, `sort`, `tail`, `cut`, `date`, `uptime`, and `df`. Jenkins job configuration consumes warning text.

## Risks and Edge Cases
The warning message uses `$type` while the global variable is initialized as `TYPE`; later `type=time/count` creates a lowercase variable, which works but is confusing. The usage text has typos. `AvgValues` divides by word count; empty input would fail, though recent appended row usually prevents that. Disk load is stubbed to `0.0`.

## Test Signals
Run in a fake Jenkins environment with temporary `STATE_DIR` after patching or overriding path, append enough values to validate v3/v20/v100 logic, and assert warning behavior for time and count metrics.
