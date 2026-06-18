# sources/test-tools/syzkaller/syz-ci/jobs_test.go

Purpose: unit tests for patch-test result aggregation.

Important APIs/types/functions: `TestAggregateTestResults`.

Control flow: constructs lists of `instance.EnvTestResult` containing success, crash, test error, infra error, and raw output combinations; calls `aggregateTestResults`; compares selected crash title, returned error string, and raw output.

State and persistence: no persistent state.

Dependencies and integration points: validates local adaptation of `instance.AggregateTestResults` to dashboard patch-test semantics.

Risks: tests focus on aggregation only, not actual VM execution.

Test signals: ensures crash reports take precedence over infra/test noise and test errors are returned rather than treated as bug reproduction.
