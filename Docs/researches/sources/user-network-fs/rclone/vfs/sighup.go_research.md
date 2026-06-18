<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup.go -->
# sources/user-network-fs/rclone/vfs/sighup.go

## Purpose
Provides supported-platform SIGHUP notification wiring for VFS directory-cache reload.

## Important APIs, Types, and Functions
Defines `NotifyOnSigHup(sighupChan chan os.Signal)` for builds excluding Plan 9 and JavaScript/WASM.

## Control Flow
The function calls `signal.Notify(sighupChan, syscall.SIGHUP)`. `VFS.signalHandler` in `vfs.go` consumes that channel and forgets the root directory cache on signal.

## State and Persistence Behavior
No persisted state. Registers process-level signal delivery for the provided channel until normal signal package semantics are changed elsewhere.

## Dependencies and Integration Points
Depends on `os/signal` and `syscall`. Integrated by `New`, which starts a signal handler goroutine for each VFS instance.

## Risks and Edge Cases
Multiple active VFS instances each register a channel for SIGHUP, so one signal can prompt multiple cache forgets. There is no explicit `signal.Stop` in this helper. Unsupported targets use the no-op file.

## Test Signals
No direct tests in this subset. Behavior is indirectly tied to `VFS.signalHandler`, which is also not directly tested here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup.go -->
