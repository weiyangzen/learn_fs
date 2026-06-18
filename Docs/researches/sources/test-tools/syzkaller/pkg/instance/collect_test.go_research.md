## sources/test-tools/syzkaller/pkg/instance/collect_test.go

Purpose: table-driven validation for `CollectRuns`.

Important APIs/types/functions: `mockRunner` and `TestCollectRuns`.

Control flow: mock attempts return scripted result batches/errors; assertions check valid result count, number of attempts, and expected errors.

State and persistence: in-memory mock state tracks calls and scripted outputs.

Dependencies and integration: directly exercises `TestError` infra/non-infra and `CrashError` classification.

Risks: tests do not run real VMs; they validate scheduler/classifier semantics only.

Test signals: good coverage for retry boundaries and batching behavior.
