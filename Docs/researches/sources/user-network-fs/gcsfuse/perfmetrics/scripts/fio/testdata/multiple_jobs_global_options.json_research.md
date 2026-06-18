## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_global_options.json

Purpose: Successful multi-job fixture where required parameters come from global options.

APIs and structure: Contains global `rw`, `numjobs`, `filesize`, `ramp_time`, and `startdelay`, with two read jobs whose job options are empty. Populated read metrics validate parser handling of repeated jobs sharing global params.

Control flow and state: No code. `_get_job_params` should use global defaults for both jobs, and `_get_start_end_times` should compute separate windows from each `job_start`.

Dependencies and risks: Requires `job options` keys even when empty because the parser only appends params inside that branch.

Test signals: Expected output is two read metric records with shared filesize/thread params.
