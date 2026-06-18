# File Research: sources/os/linux/linux/fs/xfs/xfs_log.h

## Purpose

`xfs_log.h` is the public-ish XFS log manager header used by transaction, recovery, and filesystem code outside the private log implementation. It defines log region type constants, small formatting helpers, LSN comparison, log force flags, and declarations for log lifecycle, reservation, forcing, CIL callback, and shutdown APIs.

## Region Type Definitions

The file defines `XLOG_REG_TYPE_*` constants used in `struct xfs_log_iovec.i_type` to identify log payload regions. Types cover buffers, inode formats and forks, quota records, transaction/log-record headers, unmount and commit records, inode create records, reverse-mapping intent/done records, refcount intent/done records, block mapping intent/done records, attribute intent/done/name/value records, and exchange-range intent/done records.

`XLOG_REG_TYPE_MAX` is `34`, matching the highest region constant in this header. `XFS_LOG_VEC_ORDERED` is `-1`, used by item sizing code to mean an ordered item that must be tracked for ordering/unpinning but has no data regions to write.

## Formatting Helpers

- `xlog_calc_iovec_len(int len)` rounds arbitrary payload sizes to `uint32_t` alignment for log iovec storage.
- `xlog_format_start()` and `xlog_format_commit()` are declared here and implemented in `xfs_log_cil.c`; together they reserve and finalize one formatted log-vector region.
- `xlog_format_copy()` wraps start/copy/commit for callers that already have a contiguous structure to copy into a formatted log vector.

These helpers hide the opheader and alignment details from individual log item formatters.

## LSN Comparison

`_lsn_cmp()` compares two `xfs_lsn_t` values by cycle first and block second. The `XFS_LSN_CMP(x, y)` macro maps to this helper. Return values are negative, positive, or zero, but use sentinel magnitudes `-999` and `999` rather than strict `-1`/`1`; callers use sign semantics.

The function avoids treating the LSN as a single host-endian 64-bit integer, which matters because LSN components are encoded as cycle and block fields.

## Public API Declarations

Lifecycle and recovery-facing declarations:

- `xfs_log_mount()`
- `xfs_log_mount_finish()`
- `xfs_log_mount_cancel()`
- `xfs_log_unmount()`
- `xfs_log_quiesce()`
- `xfs_log_clean()`
- `xfs_log_work_queue()`

Reservation and ticket declarations:

- `xfs_log_reserve()`
- `xfs_log_regrant()`
- `xfs_log_ticket_get()`
- `xfs_log_ticket_put()`

Force, tail, and validation declarations:

- `xfs_log_force()`
- `xfs_log_force_seq()`
- `xlog_assign_tail_lsn()`
- `xlog_assign_tail_lsn_locked()`
- `xfs_log_space_wake()`
- `xfs_log_check_lsn()`
- `xfs_log_writable()`

CIL/shutdown related declarations:

- `xlog_cil_process_committed()`
- `xfs_log_item_in_current_chkpt()`
- `xlog_force_shutdown()`

## Constants

`XFS_LOG_SYNC` is the single public force flag and requests synchronous forcing of in-core log state to disk. Calls without this flag may initiate writeout without waiting for stable completion.

## Research Notes

This header deliberately keeps only the stable cross-module surface. Most log internals, including iclog states, CIL structures, tickets, grant heads, and helper implementations, live in `xfs_log_priv.h` and the C files. The region type list is a useful map of every logical payload family the XFS journal can carry.
