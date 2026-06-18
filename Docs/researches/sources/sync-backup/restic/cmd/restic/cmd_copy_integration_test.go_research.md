# sources/sync-backup/restic/cmd/restic/cmd_copy_integration_test.go

Purpose: integration tests for cross-repository snapshot copy.

Important helpers/tests: `testRunCopy` configures source/destination global options via `SecondaryRepoOptions`. `TestCopy` creates three backups, copies them, checks destination integrity, restores source/destination snapshots for content comparison, and verifies batching produced expected pack counts. `TestCopyIncremental` verifies repeated copy skips existing snapshots and later copies only new snapshots, including reverse direction. `TestCopyUnstableJSON` covers copied metadata containing difficult symlink JSON. `TestCopyToEmptyPassword` verifies copying into a repository with no password.

State/persistence: creates two repositories, writes snapshots/blobs into both, restores content to temp dirs, and reads pack/blob counts.

Dependencies/integration: backup, restore, check, list, repository pack-handle listing, and progress helpers.

Risks/test signals: asserts pack-count expectations that can change if batching/pack sizing changes. Provides strong coverage that copy preserves file content and avoids duplicate snapshot copies.
