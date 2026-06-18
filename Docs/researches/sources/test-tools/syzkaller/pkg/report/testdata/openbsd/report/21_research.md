# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/21

## Purpose

This OpenBSD fixture expects `panic: vop_generic_badop`, is typed `DoS`, and is marked `SUPPRESSED: Y`. It captures a VFS bad-operation panic during UFS mkdir/writeback logic.

## Important APIs, Types, and Functions

Reporter behavior includes panic-title extraction, DoS and suppressed metadata parsing, DDB repeated-trace handling, and post-crash lock context capture. Kernel functions include `vop_generic_badop`, `VOP_STRATEGY`, `bwrite`, `VOP_BWRITE`, `ufs_mkdir`, `VOP_MKDIR`, `domkdirat`, `syscall`, and `Xsyscall`; later lock stacks mention `ffs_update`, `ffs_inode_alloc`, `vfs_lookup`, and `vn_closefile`.

## Control Flow

The panic occurs when a generic bad VOP handler is invoked through `VOP_STRATEGY` while writing a buffer during `ufs_mkdir`. The syscall path is `mkdirat` through `domkdirat` and `VOP_MKDIR`. DDB repeats the trace, then `show all locks` records multiple filesystem lock acquisition stacks.

## State and Persistence Behavior

The fixture stores process metadata, VFS operation stack, lock stacks, registers, and allocator/pool diagnostics. The stable state is the panic string and VFS operation path. Suppression and DoS metadata should remain attached to the parsed report.

## Dependencies and Integration Points

This integrates OpenBSD VFS panic parsing with syzkaller suppression handling. It also tests that post-panic lock diagnostics are retained as evidence but do not change the primary panic title.

## Risks and Edge Cases

The report is suppressed despite being a panic, so consumers must preserve both facts. Generic VFS helper names can be broad; however, the expected title is the panic string, not a deeper `ufs_mkdir` title. Repeated DDB traces must not create duplicate crashes.

## Test Signals

A passing test returns `panic: vop_generic_badop`, marks `TYPE: DoS` and suppressed state, and includes the `VOP_STRATEGY` to `domkdirat` trace.
