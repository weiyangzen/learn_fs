# sources/test-tools/syzkaller/pkg/vminfo/linux_test.go

## Purpose

This file tests Linux VM-info syscall filtering and machine-info formatting.

## Important APIs, Types, And Functions

`TestLinuxSyscalls` builds a Linux/amd64 checker with virtual `/proc/version` and `/proc/filesystems`, feeds successful executor results, and verifies expected disabled calls. `TestReadKVMInfo` validates host KVM info formatting on Linux. `TestCannedCPUInfoLinux`, `checkCPUInfo`, `cannedTest`, and `cpuInfoTests` validate CPU info parsing for canned and host data.

## Control Flow, State, Dependencies, And Integration

`TestLinuxSyscalls` runs `Checker.Run` concurrently with `createSuccessfulResults`, so executor queue behavior is part of the signal. CPU tests build virtual filesystems from canned data. Host KVM/CPU checks are conditional on runtime OS.

## Risks And Test Signals

The test catches accidental broad disabling of Linux syscalls, especially mount variants and architecture-specific KVM calls. CPU info expectations are architecture-aware and protect output shape. Host-dependent portions may reveal environmental issues rather than pure logic regressions.
