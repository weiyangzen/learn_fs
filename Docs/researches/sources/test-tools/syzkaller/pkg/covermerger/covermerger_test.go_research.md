# sources/test-tools/syzkaller/pkg/covermerger/covermerger_test.go

Purpose: integration and unit tests for CSV merging, JSONL generation, Spanner save compatibility, manager aggregation, and line-mapping behavior across commits.

Important APIs/types/functions: `TestMergeCSVWriteJSONL_and_coveragedb_SaveMergeResult`, `TestMergerdCoverageRecords`, `TestAggregateStreamData`, `fileVersProviderMock`, `testConfig`, and `TestCheckedFuncName`.

Control flow: the JSONL test pipes `MergeCSVWriteJSONL` output through gzip into `coveragedb.SaveMergeResult` and asserts total line counts plus mutation counts. Aggregation tests feed inline or fixture BigQuery CSV rows, consume merge results from a channel, and compare JSON-encoded expected `MergeResult`s. The mock provider reads file versions from testdata repos by commit.

State and persistence: reads checked-in testdata trees and writes only pipes/buffers. Spanner is mocked.

Dependencies and integration: connects `covermerger`, `coveragedb`, gzip, Spanner mocks, and testdata integration repos.

Risks: tests rely on CSV ordering and fixture file layouts. The test name `TestMergerdCoverageRecords` is misspelled but harmless. Some aggregate comparisons omit line details for broad fixture cases.

Test signals: strong evidence for core merge semantics, especially handling deleted files/code, changed lines, added lines, zero-hit lines, and per-manager/all-manager output.
