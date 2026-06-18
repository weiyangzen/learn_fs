<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter.go -->
# sources/user-network-fs/rclone/fs/driveletter/driveletter.go

## Purpose
Non-Windows implementation of drive-letter detection.

## Important APIs, Types, And Control Flow
`IsDriveLetter` always returns false because single-letter remote names are not ambiguous with Windows drive letters on non-Windows platforms.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected by `!windows` build tag. Config UI uses it to reject names that could be confused with drive letters only where relevant.

## Risks And Test Signals
Build-tag selection is the key behavior. Direct tests are platform-dependent and not present here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter.go -->
