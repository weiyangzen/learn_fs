## sources/user-network-fs/go-fuse/fs/windows_test.go

Purpose: tests Windows-emulation behavior implemented by the loopback layer.

Important APIs/types/functions: `TestWindowsEmulations` mounts the `WindowsNode` example wrapper, opens a file through the mount, and validates unlink behavior around an open handle.

Control flow: creates a loopback-backed mount, writes and reads a file, opens it, checks that `syscall.Unlink` fails while the file is open, closes the handle, waits briefly for FUSE `RELEASE`, and verifies unlink then succeeds.

State and persistence: temp backing directory persists file contents during the test. Runtime state includes open file handles and loopback node bookkeeping.

Dependencies and integration: connects `fs` loopback behavior with Windows compatibility options and kernel open/release sequencing.

Risks and test signals: protects cross-platform busy-delete semantics. Regressions usually indicate open-count tracking, node wrapping, release ordering, or unlink policy drift.
