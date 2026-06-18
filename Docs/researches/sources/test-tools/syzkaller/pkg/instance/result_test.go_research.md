## sources/test-tools/syzkaller/pkg/instance/result_test.go

Purpose: validates result aggregation ranking.

Important APIs/types/functions: `TestAggregateTestResults`.

Control flow: table-driven cases pass result slices with nil errors, ordinary errors, `CrashError`s with/without report bytes, and empty input; assertions check selected result or expected error.

State and persistence: none.

Dependencies and integration: exercises `report.Report` payload-sensitive ranking.

Risks: limited to policy examples but directly covers the important precedence order.

Test signals: strong unit coverage for aggregation behavior.
