
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_create_test.go

## Purpose
Covers broad `snapshot create` CLI behavior: normal snapshot/list flows, JSON manifest output, source grouping, tag filtering and validation, checkpoint interval validation, start/end time overrides, cache-directory exclusion, `.kopiaignore` semantics, `--all` behavior, stdin stream snapshots, flush-per-source indexing, source override parsing, and invalid flag combinations.

## Important APIs, Types, And Functions
- `TestSnapshotCreate` creates snapshots across multiple sources, reconnects repositories, validates JSON `snapshot.Manifest` IDs/root entries, tests `--max-results`, and verifies `--ignore-identical-snapshots`.
- `TestTagging` and `TestTaggingBadTags` verify tag filtering and invalid duplicate/malformed tags.
- `TestSnapshotInterval` validates max accepted checkpoint interval.
- `TestStartTimeOverride`, `TestEndTimeOverride`, and `TestInvalidTimeOverride` verify time parsing and ordering.
- `TestSnapshottingCacheDirectory` confirms cache marker directories snapshot as empty.
- `TestSnapshotCreateWithIgnore` is a table-driven `.kopiaignore` suite covering recursive ignores, negation, rooted/unrooted rules, multiple ignore files, comments, trailing spaces, and empty directories.
- `TestSnapshotCreateWithStdinStream` snapshots a stdin stream as a named file and restores it.
- `TestSnapshotCreateAllFlushPerSource`, `TestSnapshotCreateAllSnapshotPath`, and `TestSnapshotCreateWithAllAndPath` verify `--all` flush counts, manual policies from overridden sources, path normalization, and invalid `--all` plus path.
- Helpers include `appendIfMissing`, `testFileEntry`, and `createFileStructure`.

## Control Flow
Each test creates a temporary filesystem repo, runs CLI operations, and inspects either human output line counts or JSON outputs parsed with `testutil.MustParseJSONLines`. Ignore-rule tests synthesize directory trees, snapshot them, recursively list repository entries from root object IDs, expand expected directory paths, sort, and compare.

## State And Persistence Behavior
Persists snapshot manifests, source policies, global policies, content/index metadata blobs, cache marker state, and manual scheduling policies. `--stdin-file` creates a synthetic snapshot root containing streamed content. `--flush-per-source` is validated by counting index blobs and metadata blobs before and after `--all`.

## Dependencies And Integration Points
Uses `cli.SnapshotManifest`, `snapshot.Manifest`, `policy.TargetWithPolicy`, `cachedir.CacheDirMarkerFile`, `clitestutil`, `testenv`, `testutil`, and shared data dirs. It integrates CLI parsing, repository content/index storage, ignore evaluation, policy storage, and restore.

## Risks And Edge Cases
Large table-driven ignore tests are sensitive to path normalization and directory inclusion rules. `TestSnapshotCreateAllSnapshotPath` has platform-specific Windows path expectations. `TestSnapshotCreateWithStdinStream` depends on runner stdin plumbing and exact byte restoration. Line-count assertions can be brittle if user-facing CLI output formatting changes.

## Test Signals
High coverage for core snapshot creation UX and repository-side effects. Strong signal for ignore rules, policy side effects, JSON output contracts, and `--all` batching behavior.
