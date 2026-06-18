# sources/test-tools/syzkaller/vm/cuttlefish/cuttlefish.go

## Purpose

`cuttlefish.go` layers Android Cuttlefish device management on top of the GCE VM backend. It creates a GCE worker, launches a Cuttlefish Android instance inside it, and proxies syzkaller operations through host SSH and device ADB.

## Important APIs, Types, and Functions

Types are `Pool` and `instance`; constants are `deviceRoot` and `consoleReadCmd`. Important functions are `ctor`, `Pool.Count`, `Pool.Create`, `sshArgs`, `runOnHost`, `Copy`, `Forward`, `Close`, `Run`, and `Diagnose`.

## Control Flow

`ctor` creates an underlying `gce.Pool` configured to read Cuttlefish kernel logs. `Create` creates a GCE instance, starts `launch_cvd`, waits for ADB, roots the Android device, mounts debugfs, and creates `/data/fuzz`. `Copy` copies to the GCE host then `adb push`es into the device. `Forward` sets up host forwarding through the GCE backend, starts `socat` on the host, then repeatedly tries `adb reverse` to expose a device-local port. `Run` executes the command through `adb shell` inside `deviceRoot`.

## State and Persistence Behavior

The wrapper stores the underlying GCE instance and host SSH metadata. It creates Cuttlefish runtime state on the GCE VM, pushes files under `/data/fuzz`, and starts background forwarding processes on the host.

## Dependencies and Integration Points

It depends on the `gce` backend, host SSH, Cuttlefish binaries/images (`launch_cvd`, `bzImage`, `initramfs.img`), ADB, `socat`, and `vmimpl.Instance` methods.

## Risks and Test Signals

The flow assumes a specific Cuttlefish host layout and command syntax. Quoting in `sshArgs`/`runOnHost` is simple and command-string based. `socat` background lifetime is not explicitly tracked. Integration tests should cover launch failure, ADB wait/root failure, debugfs setup, copy/push, forward/reverse retries, and cleanup through underlying GCE close.
