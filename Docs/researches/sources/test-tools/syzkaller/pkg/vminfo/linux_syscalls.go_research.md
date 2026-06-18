# sources/test-tools/syzkaller/pkg/vminfo/linux_syscalls.go

## Purpose

`linux_syscalls.go` implements Linux-specific syscall availability checks. It decides whether syzkaller syscall descriptions should be enabled for a VM based on filesystems, devices, sandbox mode, architecture, kernel version, and trial executions.

## Important APIs, Types, And Functions

`linux.syscallCheck` selects a custom check from `linuxSyscallChecks` or falls back to executing the plain syscall. Custom checks include `linuxSupportedLSM`, `linuxSyzOpenDevSupported`, filesystem/mount checks, socket checks, KVM arch checks, pkeys, net injection, USB/VHCI/Wi-Fi/USBIP, BTF, ublk, genetlink, and kernel-version requirements. `matchKernelVersion` parses `/proc/version`.

## Control Flow, State, Dependencies, And Integration

The checks use `checkContext` helpers to read VM snapshot files or submit tiny executor programs. Many pseudo-syscalls are allowed unconditionally, while others require root/sandbox none or device nodes. The map keys are syscall base names, so variants share logic.

## Risks And Test Signals

Several paths panic if syscall descriptions violate assumptions such as constant socket family or string filesystem arguments. Device checks may be time-sensitive because some nodes appear only after setup. Kernel version parsing rejects minor `0`, which may be intentional but is strict. `vminfo/linux_test.go` exercises mount filtering, KVM arch disabling, filesystem checks, and feature success under synthetic executor results.
