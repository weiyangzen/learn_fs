# sources/test-tools/syzkaller/vm/adb/adb.go

## Purpose

`adb.go` implements the syzkaller VM backend for Android devices reachable through ADB. It manages configured devices, repair and reboot, console association, battery checks, binary copy, adb reverse forwarding, and merged runtime output.

## Important APIs, Types, and Functions

Key types are `Device`, `Config`, `Pool`, and `instance`. The backend registers as `adb`. Important functions include `loadDevice`, `ctor`, `Pool.Count`, `Pool.Create`, `parseAdbOutToInt`, `findConsole`, `findConsoleImpl`, `Forward`, `adb`, `adbWithTimeout`, `waitForBootCompletion`, `markBootSuccessful`, `repair`, `runScript`, `waitForSSH`, `checkBatteryLevel`, `getBatteryLevel`, `Close`, `Copy`, `isRemoteCuttlefish`, `Run`, and `Diagnose`.

## Control Flow

`ctor` loads defaults and validates ADB binary and device identifiers. `Create` loads the indexed device, repairs it, discovers or configures console access, checks battery level, clears stale `/data/syzkaller*` files, and lowers `kptr_restrict`. `repair` optionally runs a repair script, waits for ADB, reboots, roots the device, waits for boot-service completion, marks the boot successful, mounts debugfs, and runs startup script. `Run` opens a console source, starts `adb shell cd /data; command`, merges console/stdout/stderr streams, and returns `vmimpl.Multiplex` channels.

## State and Persistence Behavior

Per-instance state stores adb binary, serial, console path/command, a close channel, debug flag, and timeout scale. Package-level console caches map devices to consoles. It mutates target device state by rebooting, rooting, mounting debugfs, deleting `/data/syzkaller*`, pushing binaries to `/data`, changing permissions, and changing kernel printk/kptr settings.

## Dependencies and Integration Points

It depends on Android ADB, `vmimpl` console/multiplex helpers, `osutil`, target timeouts, and optional remote Cuttlefish kernel-log helpers. It implements the `vmimpl.Pool` and `vmimpl.Instance` contracts consumed by syz-manager.

## Risks and Test Signals

Runtime behavior is environment-heavy: ADB hangs, reboot semantics, boot service names, root availability, battery service, console discovery races, and remote Cuttlefish IP handling can all fail. `Close` closes a channel without guarding double close. Tests currently cover config and device parsing; integration tests need real or simulated ADB devices for repair, console discovery, forwarding, copy, and merged output behavior.
