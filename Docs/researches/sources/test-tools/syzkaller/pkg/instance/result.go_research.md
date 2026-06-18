## sources/test-tools/syzkaller/pkg/instance/result.go

Purpose: selects the most relevant result from multiple VM test runs.

Important APIs/types/functions: `AggregateTestResults`, rank constants, and `resultRank`.

Control flow: rejects empty input, ranks each `EnvTestResult`, prefers higher rank, and for equal rank either last or first depending on category. Crash with report ranks highest, then crash, success, then generic error. Success/errors prefer last; crashes prefer first.

State and persistence: none.

Dependencies and integration: uses `CrashError` and `EnvTestResult` from `instance.go`.

Risks: ranking policy encodes product semantics: transient errors are ignored in favor of success, but any crash dominates. A crash report with empty report bytes is ranked below a report with content.

Test signals: `result_test.go` covers ordering and tie behavior.
