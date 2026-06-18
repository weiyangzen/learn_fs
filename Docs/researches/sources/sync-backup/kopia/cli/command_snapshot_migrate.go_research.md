<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_migrate.go -->
# sources/sync-backup/kopia/cli/command_snapshot_migrate.go

## Purpose
Implements `snapshot migrate`, which copies snapshots and optionally policies from a source repository configuration into the currently connected destination repository.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotMigrate`, `openSourceRepo`, `migratePoliciesForSources`, `migrateAllPolicies`, `migrateSinglePolicy`, `findPreviousSnapshotManifestWithStartTime`, `migrateSingleSource`, `migrateSingleSourceSnapshot`, `filterSnapshotsToMigrate`, and `getSourcesToMigrate`.

## Control Flow
`run` opens the source repo with persisted or prompted password, selects sources, starts shared progress, registers termination cancellation over active uploaders, migrates policies if requested, and migrates sources in goroutines bounded by a semaphore. Each snapshot migration skips incomplete or already migrated snapshots, uploads source snapshotfs roots into the destination, preserves start/end/description, and saves complete manifests.

## State And Persistence Behavior
Persistent writes affect destination repository objects, snapshot manifests, and optionally policy records. Source repository is read-only and closed at the end.

## Dependencies And Integration Points
Integrates source/destination repository APIs, password persistence, policy APIs, snapshotfs roots, upload.Uploader, progress services, and cancellation handling.

## Risks And Edge Cases
Errors inside worker goroutines are logged but not returned from `run`, so a migration can finish with logged failures but nil error. Concurrency shares `destRepo` across uploaders. Existing detection uses source/start time and may skip divergent roots with same timestamp.

## Test Signals
Tests should cover all/specific source selection, latest-only, policy overwrite behavior, duplicate skip, incomplete skip, worker error propagation expectations, cancellation, and ignore-rule toggling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_migrate.go -->
