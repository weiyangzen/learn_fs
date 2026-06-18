# sources/user-network-fs/rclone/lib/terminal/hidden_other.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_other.go -->
## sources/user-network-fs/rclone/lib/terminal/hidden_other.go

Purpose: non-Windows implementation of console hiding.

Important APIs and control flow: `HideConsole()` is a no-op on all non-Windows builds.

State, dependencies, and integration: no state or imports. It preserves a cross-platform API for callers that hide the console on Windows.

Risks and test signals: no behavior to test. Correctness is build-tag selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_other.go -->
