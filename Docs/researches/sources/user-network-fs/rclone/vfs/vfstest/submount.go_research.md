# sources/user-network-fs/rclone/vfs/vfstest/submount.go

## Purpose
Implements the subprocess mount orchestration used by functional tests to avoid in-process kernel/FUSE deadlocks.

## APIs, Flow, And State
The `-run-mount` flag carries JSON-encoded `runMountOpt`. `startMountSubProcess` either creates a direct VFS-backed `Oser` or re-execs the test binary, wires stdin/stdout, and waits for a `STARTED` line. `startMount` decodes options, opens the remote from cache, mounts through `mountlib`, serves text commands on stdin, and unmounts on exit. `doMountCommand` handles `waitForWriters`, `forget`, and `exit`. Parent helpers send commands, wait for writer drain, forget directory cache entries, and unmount with retry and VFS cache cleanup.

## Dependencies And Integration
Depends on `mountlib`, `cache.Get`, `fstest`, VFS, and the `Run` harness. It bridges test process control and mounted filesystem lifecycle.

## Risks And Test Signals
Risks include subprocess startup hangs, scanner/protocol desynchronization, mount cleanup failures, and platform-specific mount path selection. Functional test success and cleanup are the main signals; failures are fatal to avoid leaving inconsistent mounts.
