# sources/user-network-fs/samba/source4/ntvfs/common/init.c

## Purpose

`init.c` provides the initialization entry point for the NTVFS common support subsystem.

## Important APIs, Types, and Functions

The only exported function is `ntvfs_common_init()`, which calls `sys_notify_init()`.

## Control Flow

Subsystem initialization delegates directly to the system notify backend initializer and returns its `NTSTATUS`.

## State and Persistence Behavior

No state is persisted by this file. Any state allocation or backend registration occurs inside the sys-notify layer.

## Dependencies and Integration Points

It includes `ntvfs/sysdep/sys_notify.h` and is built into the `ntvfs_common` subsystem with brlock, opendb, and notify support.

## Risks and Edge Cases

Failure in `sys_notify_init()` prevents common NTVFS initialization. Since the file does no logging or fallback, diagnostics depend on the sys-notify implementation.

## Test Signals

Build and startup tests should confirm `ntvfs_common_init()` is called and that sys-notify backends initialize successfully across supported platforms.
