## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_global_ramp_time.json

Purpose: FIO fixture for ramp-time fallback behavior.

APIs and structure: Global options omit `ramp_time`; at least one job supplies a job-level `ramp_time` such as `20s` and may override rw/filesize/thread params.

Control flow and state: No code. It lets tests assert `_get_global_ramp_time` returns 0 and `_get_job_ramp_time` reads the job value.

Dependencies and risks: Parser start/end calculations depend on this distinction. Changing ramp times requires expected test updates.

Test signals: Unit tests expect global ramp time 0 and job ramp time 20000 ms.
