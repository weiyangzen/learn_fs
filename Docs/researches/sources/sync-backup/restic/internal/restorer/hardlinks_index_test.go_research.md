<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index_test.go -->
# sources/sync-backup/restic/internal/restorer/hardlinks_index_test.go

## Purpose
Tests the generic `HardlinkIndex` API from the external `restorer_test` package.

## Important APIs and Control Flow
`TestHardLinks` creates an index, adds two inode/device mappings, verifies values and existence checks, then removes one mapping and verifies it is absent. The control flow is direct API exercise without filesystem interaction.

## State, Persistence, Dependencies, and Integration
State is a test-local map inside the index. It depends on exported `restorer.NewHardlinkIndex` and shared equality helpers.

## Risks and Test Signals
The test catches basic keying regressions but does not cover full restore hardlink creation; platform restore tests cover that integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index_test.go -->
