<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_unix.go -->
# sources/user-network-fs/rclone/fs/daemon_unix.go

## Purpose
Unix daemonization marker helper.

## Important APIs, Types, And Control Flow
Defines `DaemonMarkVar` and `DaemonMarkChild`. `IsDaemon` returns true when the process environment variable `_RCLONE_DAEMON_` equals `_rclone_daemon_`.

## State And Persistence
Reads process environment only; no files are touched.

## Dependencies And Integration Points
Selected on non-Windows, non-Plan9, non-JS builds. The process-spawning daemon code sets the marker for child processes.

## Risks And Test Signals
Any external process can set the env var, so this is a role marker, not a security boundary. Platform builds and daemon integration are the relevant tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_unix.go -->
