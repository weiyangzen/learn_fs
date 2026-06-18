# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log.h

## Purpose

`xfs_log.h` is the public-facing XFS log manager header used by the rest of XFS. It defines log region type constants, small formatting and LSN helper routines, log force flags, and prototypes for the main log manager and CIL-facing APIs.

## Region Type Constants

The header assigns numeric `XLOG_REG_TYPE_*` values for log iovec `i_type` fields. These classify journal regions for buffers, inodes, quotas, transaction headers, commit records, unmount records, deferred operation intents/dones, attribute intents, exchange mapping intents, and related payloads.

The maximum region type is `XLOG_REG_TYPE_MAX`, currently `34`. These values are part of the internal log formatting contract between transaction item formatters, log writing, and recovery.

## Formatting Helpers

`xlog_calc_iovec_len` rounds arbitrary payload lengths to `uint32_t` alignment. It is intended for item `iop_size` implementations so their sizing matches later formatting.

`xlog_format_start`, `xlog_format_commit`, and inline `xlog_format_copy` support CIL log vector formatting. The start/commit implementations live in `xfs_log_cil.c`; callers use them to reserve a typed log region, copy or write data into it, and finalize the iovec length/accounting.

## LSN Comparison

`_lsn_cmp` compares XFS log sequence numbers by cycle and block components rather than treating the value as a raw 64-bit integer. This avoids endian and layout assumptions. `XFS_LSN_CMP` aliases this helper.

The comparator returns negative, positive, or zero sentinel values, not a byte/block delta.

## Public Log APIs

The header declares:

- Mount lifecycle: `xfs_log_mount`, `xfs_log_mount_finish`, `xfs_log_mount_cancel`, `xfs_log_unmount`
- Log forcing: `xfs_log_force`, `xfs_log_force_seq`
- Tail and space management: `xlog_assign_tail_lsn`, `xfs_log_space_wake`
- Reservation lifecycle: `xfs_log_reserve`, `xfs_log_regrant`
- Ticket refs: `xfs_log_ticket_get`, `xfs_log_ticket_put`
- CIL helpers: `xlog_cil_process_committed`, `xfs_log_item_in_current_chkpt`
- Background/quiesce/clean state: `xfs_log_work_queue`, `xfs_log_quiesce`, `xfs_log_clean`
- Validation and shutdown: `xfs_log_check_lsn`, `xlog_force_shutdown`

## Research Notes

This header is a compact contract boundary. The region constants and LSN comparison helper are especially important because they must remain consistent with recovery code and transaction item formatters. Most complex implementation details are intentionally hidden in `xfs_log_priv.h`, `xfs_log.c`, and `xfs_log_cil.c`.
