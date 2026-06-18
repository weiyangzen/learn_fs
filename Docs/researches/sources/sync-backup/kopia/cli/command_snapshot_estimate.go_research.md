<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate.go -->
# sources/sync-backup/kopia/cli/command_snapshot_estimate.go

## Purpose
Implements `snapshot estimate`, which scans a local directory under effective policy rules and estimates included/excluded data size and upload duration.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotEstimate`, `estimateProgress`, `run`, and `showBuckets`. It uses `upload.Estimate`, `policy.TreeForSource`, local filesystem entry resolution, `snapshot.Stats`, and sample buckets.

## Control Flow
The command resolves the source to an absolute path, builds `snapshot.SourceInfo`, requires the entry to be a directory, loads the effective policy tree, runs estimator callbacks, prints included/excluded file buckets, excluded directories, error counts, and upload-time estimate based on `--upload-speed`.

## State And Persistence Behavior
It is read-only. It observes local filesystem metadata and repository policy state, but does not upload objects or write manifests.

## Dependencies And Integration Points
Integrates policy ignore rules, upload sampling, units formatting, localfs entry construction, and text output.

## Risks And Edge Cases
The path error message uses the `path` variable even if `filepath.Abs` fails before assignment. Upload speed is not locally checked for zero or negative values. Only directories are accepted, not single files.

## Test Signals
Tests cover included/excluded file sizes, ignore rules, excluded directories, and failure for non-directory sources.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate.go -->
