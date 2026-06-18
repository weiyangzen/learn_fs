# sources/test-tools/syzkaller/pkg/covermerger/file_line_merger.go

Purpose: maps line coverage records from their original commit file versions onto the base commit file and aggregates hit counts/details per target line.

Important APIs/types/functions: `makeFileLineCoverMerger`, `FileLineCoverMerger`, `Add`, and `Result`.

Control flow: the constructor finds the base file content in `FileVersions`; if missing, it returns `DeletedFileLineMerger`. Otherwise it initializes a `MergeResult` and builds one `LineToLineMatcher` per available repo commit. `Add` skips records with negative line numbers, counts positive-hit records as lost if no matcher exists, maps the source line to a target line, and accumulates hit count plus line details. `Result` logs lost frame counts and returns the merge result.

State and persistence: in-memory hit count maps, line detail maps, matchers, and lost-frame counters. No writes.

Dependencies and integration: depends on `lines_matcher.go`, `RepoCommit`, and logging. Used by `batchFileData`.

Risks: `SameLinePos` is called with `record.StartLine`, while matcher indexes are zero-based over split lines; production CSV `sl` appears one-based, so this relies on historical behavior and may be off by one unless upstream line numbering is zero-based in these exports. Missing commit versions drop positive hits into logs only. Negative line records are ignored even if function-level info exists.

Test signals: aggregate tests cover deleted code/file, changed lines, added lines, and zero-hit instrumentation through this merger.
