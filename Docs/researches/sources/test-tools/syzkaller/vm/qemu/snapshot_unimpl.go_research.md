# sources/test-tools/syzkaller/vm/qemu/snapshot_unimpl.go

## Purpose

`snapshot_unimpl.go` provides non-Linux stubs for QEMU snapshot acceleration so the qemu package compiles on platforms without the Linux-specific ivshmem/eventfd implementation.

## Important APIs, Types, and Functions

It defines empty `snapshot`, package-level `errNotImplemented`, and methods `snapshotClose`, `snapshotEnable`, `snapshotHandshake`, `SetupSnapshot`, and `RunSnapshot`.

## Control Flow

All snapshot operations except close return `errNotImplemented`; close is a no-op. Build tags select this file for `!linux`.

## State and Persistence Behavior

No state is stored or persisted.

## Dependencies and Integration Points

It integrates with `qemu.go` by satisfying the same method set as the Linux implementation. If snapshot mode is requested on non-Linux, QEMU argument construction or setup fails with the not-implemented error.

## Risks and Test Signals

The error message contains a spelling mistake but is otherwise straightforward. Build tests on non-Linux should verify qemu package compilation and clear failure when snapshots are enabled.
