## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_job_options.json

Purpose: Successful multi-job fixture where job-level options override or provide required params.

APIs and structure: Global options omit some required params while each job supplies `filesize`, `numjobs`, and read/write mode as needed. The expected parser output includes a read job and a write job with distinct sizes and thread counts.

Control flow and state: No executable behavior; exercises `_get_job_params` override logic and `_get_rw` dispatch to the correct `read` or `write` metrics section.

Dependencies and risks: Job options are required for parser completeness. Fixture values are tightly coupled to expected outputs in tests.

Test signals: Two metrics records, one read and one write, with job-specific params.
