# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/1

## Purpose

This OpenBSD fixture expects `panic: cleaned vnode isn't` and is typed as `DoS`. It exercises panic-title extraction from a vnode consistency failure during filesystem lookup after a `cleaned vnode` diagnostic.

## Important APIs, Types, and Functions

Syzkaller-facing items are `TITLE:`, `TYPE: DoS`, panic matching, DDB trace parsing, and line-wrap repair. Kernel functions include `getnewvnode`, `ffs_vget`, `ufs_lookup`, `VOP_LOOKUP`, `vfs_lookup`, `namei`, `dofstatat`, `syscall`, and `Xsyscall_untramp`.

## Control Flow

The transcript prints vnode metadata, panics, enters DDB, and traces from panic helpers into vnode allocation and UFS lookup. The represented system call path is `dofstatat` through name lookup, where `ffs_vget` calls `getnewvnode` and encounters a supposedly cleaned vnode that is not in the expected state.

## State and Persistence Behavior

The log stores vnode type, UFS inode number, device, link counts, mode, ownership, size, process IDs, and trace addresses. These values are diagnostic state only. Parser state should preserve the DoS classification and the stable panic string.

## Dependencies and Integration Points

This integrates OpenBSD filesystem panic parsing, VFS/UFS stack filtering, and multiline wrapped frame handling. It also connects report metadata to vulnerability classification through `TYPE: DoS`.

## Risks and Edge Cases

The panic line is preceded by a detailed diagnostic, so the parser must not title the report from `cleaned vnode:` rather than `panic:`. Wrapped `VOP_LOOKUP` and `dofstatat` lines must remain readable enough for stack evidence. The parser should not fold the OpenBSD bug-report URL into a second report.

## Test Signals

A passing test returns the exact panic title, retains type `DoS`, and includes the `getnewvnode`/`ffs_vget`/`ufs_lookup` trace as evidence.
