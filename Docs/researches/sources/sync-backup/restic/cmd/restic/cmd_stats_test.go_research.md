# sources/sync-backup/restic/cmd/restic/cmd_stats_test.go

Purpose: unit tests for the `sizeHistogram` helper used by stats debug output.

Important APIs/types/functions: `TestSizeHistogramNew`; `TestSizeHistogramAdd`; `TestSizeHistogramString`.

Control flow and state: tests construct a histogram with limit 42, verify bucket layout, add sizes 0 through 44 to assert counts/total/oversized, and compare formatted output for overflow and zero-inclusive cases.

Dependencies and integration points: uses restic test equality helpers and `ui.FormatBytes` indirectly via `String`.

Risks: exact string assertions tie the debug table format to tests. Main stats counting modes are not covered here.

Test signals: protects bucket boundary behavior, oversized tracking, and human-readable debug formatting.
