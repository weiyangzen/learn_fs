# sources/test-tools/syzkaller/pkg/coveragedb/coveragedb.go

Purpose: persists merged coverage into Spanner, queries coverage summaries/details, computes manager-unique coverage, regenerates file subsystem mappings, and deletes orphaned file rows.

Important APIs/types/functions: `HistoryRecord`, `MergedCoverageRecord`, `JSONLWrapper`, `Coverage`, `SaveMergeResult`, `ReadLinesHitCount`, mutation builders, `NsDataMerged`, `DeleteGarbage`, `FileCoverageWithDetails`, `FileCoverageWithLineInfo`, `SelectScope`, `FilesCoverageStream`, `FilesCoverageWithDetails`, `readCoverageUniq`, `IsComparable`, `UniqCoverage`, `RegenerateSubsystems`, and `getFilePaths`.

Control flow: `SaveMergeResult` decodes JSONL wrappers, creates `files` or `functions` mutations, batches every 1000 records, and appends `merge_history`. Query helpers build Spanner SQL joining `merge_history`, `files`, and `file_subsystems`. Unique coverage reads all-manager and manager-specific line details in parallel, validates comparability, then counts lines whose manager hit count equals total hit count. Garbage collection fetches valid sessions, streams file sessions, and deletes orphan batches with workers.

State and persistence: writes Spanner tables `files`, `functions`, `merge_history`, and `file_subsystems`; reads Spanner through the abstract client. Uses generated UUID sessions and current time for history records.

Dependencies and integration: central database layer for `covermerger`, heatmap rendering, file coverage rendering, and maintenance tasks. Depends on Spanner, civil dates, subsystem matchers, UUIDs, and errgroups.

Risks: `FilesCoverageWithDetails` with an empty `scope.Periods` returns nil before touching a possibly nil client, as tested. `ReadLinesHitCount` errors if more than one DB row matches. `readCoverageUniq` assumes both iterators are sorted by filepath and reports "currupted" on impossible partial-only files. Deferred iterator stops inside loops can accumulate until function return for many periods. Mutation batching is tuned but still sensitive to Spanner index mutation limits.

Test signals: `coveragedb_mock_test.go` verifies save batching and wrapper validation; `coveragedb_test.go` verifies empty and unique coverage query behavior with mocks.
