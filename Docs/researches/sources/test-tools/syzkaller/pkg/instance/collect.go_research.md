## sources/test-tools/syzkaller/pkg/instance/collect.go

Purpose: retries VM test attempts until a requested number of valid test results is collected while tolerating infrastructure failures.

Important APIs/types/functions: `RunAttempt`, `CollectRunsOpts`, and `CollectRuns`.

Control flow: validates `MaxTotal >= WantValid`, normalizes `MaxVMs`, batches attempts up to need/max VMs/remaining total, and classifies each `EnvTestResult`. Successes, crashes, and non-infra `TestError`s count as valid; infra errors are remembered but retried. If insufficient valid results are collected, returns partial valid results plus an error wrapping the last infra error.

State and persistence: local counters and result slices only.

Dependencies and integration: uses `CrashError` and `TestError` from `instance.go`; intended around `Env.Test`.

Risks: assumes attempted batch size reflects consumed attempts even if callback returns fewer results. Last infra error can be nil in unusual cases, producing a weak wrapped error.

Test signals: `collect_test.go` covers batching, retry, invalid option, and classification cases.
