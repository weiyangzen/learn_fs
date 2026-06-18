# File Research: sources/local-fs/xfsdump/common/util.c

## Role

This file implements general-purpose buffer, XFS bulkstat, inode-group, directory iteration, and numeric parsing utilities.

## Buffer Helpers

`write_buf()` adapts a manager-style get-buffer/write-buffer interface to write an existing caller buffer or a zero-filled logical buffer in chunks.

`read_buf()` adapts a manager-style read/return-buffer interface to fill or discard a caller buffer in chunks and reports the first read status.

`strncpyterm()` wraps `strncpy()` and always null-terminates the destination when size is nonzero.

## XFS Bulkstat Iteration

`bigstat_iter()` repeatedly calls `XFS_IOC_FSBULKSTAT`, filters directory/non-directory entries according to selector flags, retries unstable entries with `bigstat_one()`, invokes a caller callback per selected inode, supports optional seek and preemption callbacks, and returns syscall/preemption errors separately from callback status.

`bigstat_one()` retrieves one inode's `xfs_bstat` via `XFS_IOC_FSBULKSTAT_SINGLE`.

## Inode Group Iteration

`inogrp_iter()` uses `XFS_IOC_FSINUMBERS` to enumerate inode groups in batches and invokes a caller callback for each `xfs_inogrp`.

## Directory Iteration

`diriter()` opens a directory by filesystem handle and inode stat, reads directory entries through `getdents_wrap()`, skips `.` and `..`, calls `bigstat_one()` for each entry, skips too-large inode numbers when large-file directory entries are unavailable, and invokes the caller's callback with stat data and name.

It returns distinct states for syscall failure, callback stop, and normal completion.

## Numeric Parsing

`cvtnum()` parses integer strings with optional suffixes:

- no suffix: raw integer
- `b`: multiply by supplied block size
- `k`: multiply by 1024
- `m`: multiply by 1024 * 1024

Invalid strings return `-1`.

## Error Handling

The utility functions log many recoverable directory/stat iteration warnings and continue where possible, especially for transient inode state or unreadable directory entries.
