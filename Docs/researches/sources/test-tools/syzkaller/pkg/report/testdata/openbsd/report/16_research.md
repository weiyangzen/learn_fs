# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/16

## Purpose

This OpenBSD fixture expects `witness: userret: write`. It is a WITNESS `userret` report where the diagnostic includes the held-lock acquisition stack, allowing syzkaller to specialize the title to the write path.

## Important APIs, Types, and Functions

Reporter behavior includes WITNESS `userret` matching, stack-derived operation naming, panic matching for `witness_warn`, and DDB transcript capture. Kernel functions include `rw_enter`, `rrw_enter`, `VOP_LOCK`, `vn_write`, `dofilewritev`, `sys_write`, `witness_warn`, `userret`, `syscall`, and `Xsyscall`. Later lock dumps also mention `ptmioctl`, `vn_ioctl`, `sys_ioctl`, and `sys_fsync`.

## Control Flow

The report begins with WITNESS listing an inode lock held by a write stack. The panic happens later at `userret`, so the active trace is generic, but the preamble identifies `sys_write` as the lock acquisition path. The parser should combine these facts into the expected `witness: userret: write` title.

## State and Persistence Behavior

The fixture stores held locks for multiple processes, process states, registers, malloc tables, and pool statistics. The held inode address and unrelated processes are volatile; the stable state is that user return occurred while a write-acquired inode lock was still held.

## Dependencies and Integration Points

This integrates WITNESS lock diagnostics with semantic title refinement. It also tests that `show all locks` after the panic can contain several locks without overriding the first WITNESS subject.

## Risks and Edge Cases

If the parser looks only at the panic trace, it will title the report as generic `witness_warn` or `userret`. If it scans all locks without ordering, it may choose ioctl or fsync instead of write. The acquisition stack in the preamble is the authoritative signal.

## Test Signals

A passing test returns `witness: userret: write`, keeps the `witness_warn` panic, and includes the write stack from `vn_write` through `sys_write`.
