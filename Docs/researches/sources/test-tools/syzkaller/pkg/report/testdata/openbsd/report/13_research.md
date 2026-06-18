# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/13

## Purpose

This OpenBSD `DoS` fixture expects `panic: timeout_add: to_ticks < NUM`. It validates title generalization for a timer panic where `timeout_add` receives a negative tick count from speaker/PC speaker ioctl handling.

## Important APIs, Types, and Functions

Reporter behavior includes panic-title normalization that replaces numeric values with `NUM`, DoS metadata parsing, DDB transcript capture, and report-end handling through large `show malloc` and `show all pools` sections. Kernel functions include `timeout_add`, `pcppi_bell`, `spkrioctl`, `VOP_IOCTL`, `vn_ioctl`, `sys_ioctl`, `syscall`, and `Xsyscall`.

## Control Flow

The syscall path is `sys_ioctl` on a vnode/device, into `spkrioctl`, then `pcppi_bell`, which calls `timeout_add` with `to_ticks (-3)`. The panic enters DDB, repeats the panic and trace, then emits registers, process state, and allocator/pool data.

## State and Persistence Behavior

The source stores the negative tick value, process IDs, DDB registers, and extensive allocator/pool counters. The normalized title intentionally abstracts `-3` to `NUM` so equivalent bugs with different inputs deduplicate together.

## Dependencies and Integration Points

This integrates OpenBSD panic parsing with numeric sanitization and ioctl/device-driver stack capture. It also exercises long diagnostic sections following the actionable trace.

## Risks and Edge Cases

If numeric generalization fails, syzkaller may fragment reports by the exact tick value. If the parser prefers `pcppi_bell` or `spkrioctl`, it loses the direct failing invariant. Long pool listings should remain part of the same report, not become noise that hides the crash.

## Test Signals

A passing test returns `panic: timeout_add: to_ticks < NUM`, preserves `TYPE: DoS`, and includes the `timeout_add` to `sys_ioctl` trace.
