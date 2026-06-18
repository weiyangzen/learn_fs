<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix_test.go -->
# sources/sync-backup/restic/internal/restorer/restorer_unix_test.go

## Purpose
Covers Unix-specific restore behavior for hardlinks, progress accounting, sparse block counting, and permissions.

## Important APIs and Control Flow
`TestRestorerRestoreEmptyHardlinkedFields` verifies empty hardlinked files share an inode when possible. Progress-bar tests validate hardlink and dry-run accounting. `TestRestorePermissions` checks that `OverwriteIfChanged` and `OverwriteAlways` restore permissions after tampering. Tests create repository snapshots, restore into temp dirs, inspect `os.Stat`/`syscall.Stat_t`, and compare restore UI state.

## State, Persistence, Dependencies, and Integration
State is Unix filesystem metadata and temporary repositories. Dependencies include `repository.TestRepository`, `restoreui.Progress`, and syscall stat data.

## Risks and Test Signals
The signal is strong for Unix metadata integration, but it can vary by filesystem support for sparse blocks and hardlinks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix_test.go -->
