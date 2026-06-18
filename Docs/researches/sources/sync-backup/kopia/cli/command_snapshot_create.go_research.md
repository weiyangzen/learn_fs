<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_create.go -->
# sources/sync-backup/kopia/cli/command_snapshot_create.go

## Purpose
Implements `snapshot create`, the main local backup path. It handles source selection, all-source scheduled backups, uploader setup, tags, pins, time overrides, stdin snapshots, retention application, manual policy marking, reporting, and notifications.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotCreate`, constants `maxSnapshotDescriptionLength` and `timeFormat`, `run`, `setupUploader`, `snapshotSingleSource`, `reportSnapshotStatus`, `getLocalBackupPaths`, `shouldSnapshotSource`, `getContentToSnapshot`, `getTags`, `validateStartEndTime`, and `parseFullSource`.

## Control Flow
`run` validates flags, maybe upgrades the repo, expands `--all`, validates description/timestamps/tags, builds an uploader, iterates sources, prepares local or stdin content, uploads each source, collects errors, optionally sends a multi-snapshot notification, and flushes the repository. `snapshotSingleSource` finds previous manifests, gets the policy tree, uploads, adjusts metadata, saves the manifest unless identical snapshots are ignored, applies retention, optionally sets manual policy, flushes per source, and reports status.

## State And Persistence Behavior
It persists uploaded file/dir objects, snapshot manifests, pins, tags, descriptions, start/end time overrides, retention deletions, manual scheduling policy markers, and repository flush state. Stdin snapshots are modeled as a virtual directory with a streaming file.

## Dependencies And Integration Points
Integrates local filesystem entries, virtualfs, snapshot upload, policy trees, retention, notification templates, progress services, repository writers, and timestamp formatting.

## Risks And Edge Cases
Risks include continuing after `getContentToSnapshot` errors and then calling `snapshotSingleSource` with a nil entry, misuse of source override collapsing identities, timestamp override duration math, retention side effects after each save, and long descriptions/tags needing validation. Flush behavior differs with `--flush-per-source`.

## Test Signals
Tests should cover normal snapshots, `--all`, stdin, tags, pins, time overrides, ignored identical snapshots, fatal/ignored upload errors, notification severity, and flush behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_create.go -->
