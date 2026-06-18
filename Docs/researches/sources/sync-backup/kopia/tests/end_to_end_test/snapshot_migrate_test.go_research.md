
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_migrate_test.go

## Purpose
Tests `snapshot migrate` between repositories, including snapshot/policy count preservation, idempotence, compression effects, overwrite policies, parallel migration, and applying destination ignore rules.

## Important APIs, Types, And Functions
- `TestSnapshotMigrate` creates source snapshots/policies, adds compressible test data, migrates all snapshots to a destination repo with `--parallel=5 --overwrite-policies`, verifies counts, reruns migration as a no-op, and compares destination repository size against source.
- `TestSnapshotMigrateWithIgnores` sets an ignore policy on destination, migrates with `--apply-ignore-rules`, and verifies ignored files are omitted.
- `writeCompressibleFile` creates large repeated UUID-derived content to test compression during migration.

## Control Flow
The tests create separate `CLITest` environments sharing a runner, use the source config path as `--source-config`, then inspect destination snapshots/policies and object listing. The compression test records repository directory sizes before/after migration.

## State And Persistence Behavior
Migrates snapshot manifests, policies, content, and compressed object data between independent filesystem repositories. Destination policies can alter migrated content when ignore rules are applied.

## Dependencies And Integration Points
Uses `cli.SnapshotManifest`, `testenv`, `testutil`, `uuid`, filesystem repository storage, and format-specific suite flags.

## Risks And Edge Cases
Repository size comparison is approximate and may be affected by packing/indexing overhead. Idempotence relies on duplicate detection. Ignore-rule migration tests depend on destination policy lookup for the original source path.

## Test Signals
Strong integration signal for migration correctness, idempotence, policy copy/overwrite, and compression/ignore interactions.
