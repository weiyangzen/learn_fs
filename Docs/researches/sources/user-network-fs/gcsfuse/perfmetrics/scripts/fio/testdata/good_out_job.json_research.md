## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/good_out_job.json

Purpose: Canonical successful FIO fixture with one read job.

APIs and structure: Includes global options such as `rw=read`, `ramp_time=10s`, `runtime=60s`, `filesize=50M`, one job with `numjobs=40`, `job_start`, populated `read` metrics, zeroed `write`/`trim`, and latency percentiles required by the parser.

Control flow and state: No code; the parser uses it to verify params, start/end time calculation, required metrics, and upload-row ordering.

Dependencies and risks: Fixture values are duplicated in expected dicts in `fio_metrics_test`, so changes require test updates.

Test signals: Should produce one metrics record with start `1653027084`, end `1653027155`, filesize 50000 KB, and read metrics.
