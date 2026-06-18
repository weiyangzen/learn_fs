<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter_windows.go -->
# sources/user-network-fs/rclone/fs/driveletter/driveletter_windows.go

## Purpose
Windows implementation of drive-letter detection for config remote names.

## Important APIs, Types, And Control Flow
`IsDriveLetter` returns true only for one-character ASCII letters `a-z` or `A-Z`; all other strings are false.

## State And Persistence
Pure function with no state.

## Dependencies And Integration Points
Selected by `windows` build tag and used by config UI name validation to avoid ambiguity with paths like `C:`.

## Risks And Test Signals
Only ASCII letters count; Unicode drive-like characters are rejected. Cross-platform builds are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter_windows.go -->
