<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_other.go -->
# sources/user-network-fs/rclone/fs/daemon_other.go

## Purpose
Non-Unix daemonization adapter for Windows, Plan 9, and JavaScript builds.

## Important APIs, Types, And Control Flow
`IsDaemon` always returns false because these build targets do not use the Unix daemon marker protocol in this file.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Selected by build tags `windows || plan9 || js`; paired with `daemon_unix.go` for other platforms.

## Risks And Test Signals
Correctness depends on build tags. There are no direct tests in this subset; platform builds are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_other.go -->
