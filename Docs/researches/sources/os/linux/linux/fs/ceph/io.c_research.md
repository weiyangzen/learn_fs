# File Research: sources/os/linux/linux/fs/ceph/io.c

## Purpose

`io.c` provides small synchronization helpers that coordinate buffered and direct I/O on a Ceph inode. It is borrowed conceptually from NFS and uses `inode->i_rwsem` plus `CEPH_I_ODIRECT` in `ci->i_ceph_flags` to prevent unsafe overlap between buffered page-cache I/O and direct I/O.

## Major Interfaces

- `ceph_start_io_read()` starts a buffered read section.
- `ceph_end_io_read()` ends a buffered read section.
- `ceph_start_io_write()` starts a buffered write section.
- `ceph_end_io_write()` ends a buffered write section.
- `ceph_start_io_direct()` starts a direct I/O section.
- `ceph_end_io_direct()` ends a direct I/O section.

The start helpers return `0` on success or an interrupt error from killable rwsem acquisition. Callers must pair successful starts with the matching end helper.

## Control Flow

Buffered read starts optimistically with a shared `i_rwsem` lock. If `CEPH_I_ODIRECT` is not set, reads can proceed concurrently. If direct I/O mode is active, it drops the shared lock, takes the write lock, clears `CEPH_I_ODIRECT`, waits for existing direct I/O with `inode_dio_wait()`, and downgrades back to a read lock.

Buffered write takes the write lock immediately because buffered writes must serialize against reads, direct I/O transitions, and truncates. It calls `ceph_block_o_direct()` to clear direct I/O mode and wait for outstanding direct I/O before returning.

Direct I/O starts optimistically with a shared `i_rwsem` lock. If `CEPH_I_ODIRECT` is already set, direct I/O can proceed concurrently with other direct I/O. If not, it drops the read lock, takes the write lock, sets `CEPH_I_ODIRECT`, waits for dirty buffered page cache with `filemap_write_and_wait()`, and downgrades back to a read lock.

## Internal Helpers

`ceph_block_o_direct()` requires the write side of `i_rwsem`. It checks and clears `CEPH_I_ODIRECT_BIT` under `ci->i_ceph_lock`, uses memory barriers before/after atomic bit operations, and calls `inode_dio_wait()` if the flag was set.

`ceph_block_buffered()` also requires the write side of `i_rwsem`. It sets `CEPH_I_ODIRECT_BIT` if it was not already set and writes/waits on the mapping to drain buffered data before direct I/O proceeds. A comment notes a possible future `unmap_mapping_range()` consideration.

## Locking And Memory Ordering

The outer mode transition is serialized by `inode->i_rwsem`. The `CEPH_I_ODIRECT` flag is read or modified under `ci->i_ceph_lock`, with explicit barriers around atomic bit state changes to keep flag visibility consistent for racing readers.

The downgraded write-to-read lock pattern lets the mode switch happen exclusively while allowing same-mode I/O to run concurrently afterward.

## Dependencies

This file depends on `super.h` for `struct ceph_inode_info`, flag definitions, and `ceph_inode()`, and on `io.h` for exported prototypes. It uses Linux rwsem, inode direct-I/O wait, and page-cache writeback helpers.

## Error Handling And Risks

- All lock acquisition paths are killable and can return interrupt errors, so callers must not call end helpers after a failed start.
- Correctness depends on all buffered/direct I/O paths consistently using these helpers.
- Direct I/O mode transition waits for buffered writeback but does not unmap existing mappings; mmap coherency remains an area to verify with broader CephFS tests.
