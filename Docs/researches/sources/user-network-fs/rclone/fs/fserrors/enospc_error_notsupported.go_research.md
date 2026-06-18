<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error_notsupported.go -->
# sources/user-network-fs/rclone/fs/fserrors/enospc_error_notsupported.go

## Purpose
Plan9 fallback for no-space detection.

## Important APIs, Types, And Control Flow
`IsErrNoSpace` always returns false because Plan9 lacks `syscall.ENOSPC` support in this code path.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected by the `plan9` build tag and shares the same public function as other platforms.

## Risks And Test Signals
Plan9 cannot classify disk-full errors through this helper. Platform build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error_notsupported.go -->
