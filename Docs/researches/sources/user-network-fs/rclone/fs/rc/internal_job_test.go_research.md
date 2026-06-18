# Research: sources/user-network-fs/rclone/fs/rc/internal_job_test.go

## sources/user-network-fs/rclone/fs/rc/internal_job_test.go

Purpose: external-package tests ensuring internal `rc/panic` and `rc/fatal` behavior is safely captured by the job framework. They invoke registered calls through `jobs.NewJob`.

Control flow finds `rc/panic` or `rc/fatal`, runs it synchronously as a job, and asserts the returned error includes the original message plus panic/fatal framing and that output is an empty params map. State is limited to the global rc call registry and global job queue side effects. Dependencies are `fs/rc`, `fs/rc/jobs`, and testify. Integration signal is important because direct panic/fatal calls would otherwise crash the process; through jobs they become structured job failures with stack text. Risks covered include panic recovery and fatal-to-panic wrapping. It does not test the direct call path outside jobs, which is intentionally unsafe for these endpoints.
