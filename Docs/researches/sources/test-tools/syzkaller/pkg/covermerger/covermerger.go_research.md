# sources/test-tools/syzkaller/pkg/covermerger/covermerger.go

Purpose: merges CSV coverage rows collected across kernel commits into line coverage for a target base commit and optionally emits gzipped JSONL records for Spanner ingestion.

Important APIs/types/functions: CSV key constants, `FileRecord`, `RepoCommit`, `MergeResult`, `FileCoverageMerger`, `MergeCSVWriteJSONL`, `mergedCoverageRecords`, `bestFuncName`, `batchFileData`, `makeRecord`, `Config`, `FileMergeResult`, `MergeCSVData`, `mergeChanData`, and `groupFileRecords`.

Control flow: `MergeCSVData` reads the first CSV row as schema, streams rows into `FileRecord`s, skips repeated headers, groups contiguous records by file path, and merges groups concurrently according to `Config.Jobs`. Each file batch fetches all required file versions, builds a line merger, and emits a `FileMergeResult`. `MergeCSVWriteJSONL` concurrently consumes results, writes a description then function-line and manager/all coverage wrappers to a gzip JSON encoder, and counts instrumented/covered lines.

State and persistence: in-memory merge state; optional writer receives compressed JSONL. Source file contents are fetched through a `FileVersProvider`.

Dependencies and integration: imports `coveragedb` record types, `go-diff` indirectly through line merger, errgroup, and logging. Feeds `coveragedb.SaveMergeResult`.

Risks: grouping assumes CSV rows are ordered by `file_path`; unsorted input can produce multiple results for one file. If `Config.Jobs` is zero, no workers drain groups. `groupFileRecords` emits an empty filename group on empty input after schema. `MergeCSVWriteJSONL` encodes a raw `HistoryRecord` before JSONL wrappers, so consumers must read it separately as tests do.

Test signals: `covermerger_test.go` covers JSONL-to-Spanner integration, manager aggregation, file deletion, code deletion, line additions/changes, zero-hit instrumentation, and function-name selection.
