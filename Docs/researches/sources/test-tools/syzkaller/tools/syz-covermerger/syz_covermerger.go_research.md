<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-covermerger/syz_covermerger.go -->
# sources/test-tools/syzkaller/tools/syz-covermerger/syz_covermerger.go

## Purpose

Batch coverage merger that streams BigQuery coverage rows to merged JSONL and dashboard/GCS storage.

## Important APIs, Types, and Functions

Flags workdir/repo/commit/namespace/duration/date/rows/to-gcs/to-dashapi/client; uses `coveragedb.NewReader`, `covermerger.MergeCSVWriteJSONL`, `gcs`, `dashapi`.

## Control Flow

Initializes config and reader, optionally obtains dashboard upload URL, opens GCS writer, streams CSV through merger into JSONL, closes writer, prints coverage, then asks dashboard to save coverage.

## State and Persistence Behavior

Persists repo/cache under workdir and uploaded JSONL/coverage metadata; merging is streaming.

## Dependencies and Integration Points

Requires BigQuery/GCS/dashboard credentials, repo access, and correct row count/date inputs.

## Risks and Edge Cases

Long-running network/auth-sensitive job; without output URL it can discard JSONL; row count correctness matters.

## Test Signals

Small namespace/date integration with test bucket or mock writer; separate dashboard save test.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-covermerger/syz_covermerger.go -->
