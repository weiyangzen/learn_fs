<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index.go -->
# sources/sync-backup/restic/internal/restorer/hardlinks_index.go

## Purpose
Implements a generic hardlink index keyed by inode and device ID so restore can recognize multiple snapshot nodes referring to the same file.

## Important APIs and Control Flow
`HardlinkIndex[T]`, `NewHardlinkIndex`, `Add`, `Has`, `Value`, and `Remove` wrap a map keyed by a small inode/device struct. Restore code adds the first hardlinked file location and later uses `Has`/`Value` to create hardlinks to the already-restored target instead of duplicating content.

## State, Persistence, Dependencies, and Integration
State is an in-memory map for one restore run. It integrates with `Restorer.RestoreTo` hardlink handling and is not persisted.

## Risks and Test Signals
Risks are incorrect inode/device keys causing missed or wrong hardlink reconstruction. Tests verify add, lookup, existence, and removal behavior for generic string values.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index.go -->
