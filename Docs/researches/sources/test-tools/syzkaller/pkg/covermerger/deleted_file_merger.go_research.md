# sources/test-tools/syzkaller/pkg/covermerger/deleted_file_merger.go

Purpose: implements the `FileCoverageMerger` interface for files absent from the target base commit.

Important APIs/types/functions: `DeletedFileLineMerger`, `Add`, and `Result`.

Control flow: `Add` ignores all records. `Result` returns a `MergeResult` with `FileExists: false`.

State and persistence: stateless; no stored records.

Dependencies and integration: returned by `makeFileLineCoverMerger` when the base file version is missing. `mergedCoverageRecords` drops file results where `FileExists` is false.

Risks: all historical coverage for deleted files is intentionally suppressed from database output. If a missing base file is caused by provider failure rather than deletion, coverage is lost silently aside from provider logs.

Test signals: `covermerger_test.go` includes a `file deleted` aggregation case that expects `FileExists: false`.
