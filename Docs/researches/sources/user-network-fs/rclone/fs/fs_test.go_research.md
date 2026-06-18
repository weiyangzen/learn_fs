<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs_test.go -->
# sources/user-network-fs/rclone/fs/fs_test.go

## Purpose
Tests feature reflection helpers defined in `features.go`.

## Important APIs, Types, And Control Flow
Tests verify `Disable` clears function and bool features case-insensitively, `List` includes known feature names, `Enabled` reports bool/function status for all fields, and `DisableList` applies multiple names.

## State And Persistence
Local `Features` instances only.

## Dependencies And Integration Points
Uses function fields matching optional feature signatures.

## Risks And Test Signals
Good signal for reflection helpers. It does not test `Fill`, `Mask`, wrapper propagation, or unwrapping helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs_test.go -->
