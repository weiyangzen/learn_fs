# sources/sync-backup/kopia/tests/end_to_end_test/content_info_test.go

## Purpose
Tests content listing, summaries, stats, and deleted-content visibility after explicit content deletion.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestContentListAndStats` uses `snapshot.Manifest`, `content.Info`, and `containsLineStartingWith`.

## Control Flow
The test creates a repository, verifies deleted-only list is empty, sets compression, writes a compressible file, snapshots with JSON output, derives the root content ID, checks it appears in normal list modes and summary, runs stats, sleeps to separate timestamps, deletes the content, then verifies it disappears from normal list modes and appears in deleted list modes.

## State and Persistence Behavior
Creates content and a snapshot manifest, then writes deletion metadata for the content ID. Timestamp separation matters because create/delete in the same second can resolve unexpectedly.

## Dependencies and Integration Points
Exercises content CLI list/stats/delete, snapshot JSON output, object-to-content ID conversion, and compression metadata listing.

## Risks
Relies on textual `content list` prefixes and second-level timestamp behavior. Deleting the root content intentionally corrupts snapshot restoreability but is scoped to the test repo.

## Test Signals
Validates content visibility transitions between active and deleted lists plus long/compressed/summary listing modes.
