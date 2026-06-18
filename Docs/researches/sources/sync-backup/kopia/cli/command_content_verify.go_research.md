# sources/sync-backup/kopia/cli/command_content_verify.go

## Purpose
Content verification command that validates content-to-blob backing data, optionally downloading a percentage or all content, with parallel iteration and ETA progress.

## APIs, Types, and Functions
Important APIs include types `commandContentVerify`; functions/methods `setup`, `run`, `getTotalContentCount`; Kingpin command(s) verify: Verify that each content is backed by a valid blob; flags parallel: Parallelism, full: Full verification (including download), include-deleted: Include deleted contents, download-percent: Download a percentage of files [0.0 .. 100.0], progress-interval: Progress output interval.

## Control Flow, State, and Persistence
Control flow registers command(s) verify: Verify that each content is backed by a valid blob, binds flags parallel: Parallelism, full: Full verification (including download), include-deleted: Include deleted contents, download-percent: Download a percentage of files [0.0 .. 100.0], progress-interval: Progress output interval, then runs through a direct repository read action. The implementation verifies content backing data. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sync, sync/atomic, time, github.com/pkg/errors, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/repo, kopia/repo/content plus external packages context, sync, sync/atomic, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_content_verify_test.go` provides direct coverage.
