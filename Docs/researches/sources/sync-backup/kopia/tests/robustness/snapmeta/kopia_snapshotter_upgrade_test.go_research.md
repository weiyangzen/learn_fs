<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter_upgrade_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter_upgrade_test.go

This file tests or gates the Kopia snapshotter repository-upgrade path. It exercises repository status retrieval and upgrade behavior under the robustness snapshotter wrapper, typically controlled by environment because upgrades are integration-heavy.

The main control-flow signal is that `KopiaSnapshotter.GetRepositoryStatus` can parse `repository status --json` and `UpgradeRepository` can execute the CLI upgrade command while setting and clearing `KOPIA_UPGRADE_LOCK_ENABLED`.

Risks include tests being skipped when `KOPIA_EXE` or upgrade env is absent, and real repository format changes being destructive or non-repeatable. Integration is with the single-client harness `TestMain`, which also contains upgrade logic.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter_upgrade_test.go -->
