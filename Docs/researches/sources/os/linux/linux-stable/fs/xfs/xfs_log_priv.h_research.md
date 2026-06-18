# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log_priv.h

## Purpose

`xfs_log_priv.h` defines the private structures, state constants, helper functions, and internal prototypes shared by XFS log implementation files. It is the internal contract for `xfs_log.c`, `xfs_log_cil.c`, recovery code, and related transaction/log components.

## Core Structures

`struct xfs_log_iovec` describes a typed log region: address, byte length, and region type.

`struct xfs_log_vec` groups iovecs for one log item in the CIL. It tracks list linkage, ordering id, iovec array, owning item, formatted buffer, used bytes, and allocation size.

`struct xlog_ticket` tracks a transaction’s log reservation: queue linkage, owning task, transaction id, refcount, current and unit reservations, count fields for permanent reservations, flags, and iclog header accounting.

`struct xlog_in_core` is an in-core log buffer. It contains waitqueues, ring pointers, owning log pointer, size/offset/state/flags, data and header pointers, callback list, refcount, semaphore, completion work, bio, and bio vectors. The layout deliberately separates hot fields onto cachelines to reduce contention.

`struct xfs_cil_ctx` is a CIL checkpoint context. It records sequence, start and commit LSNs, commit iclog, checkpoint ticket, aggregate space, busy extents, log item/vector lists, callback linkage, push work, order id, and CPU mask for per-CPU contributors.

`struct xlog_cil_pcp` holds per-CPU CIL accumulation: space used, reservation space, busy extents, and log items.

`struct xfs_cil` owns the active CIL state: current context, push workqueue, locks, push sequence, committing list, waitqueues, current sequence, and per-CPU storage.

`struct xlog` is the main log object. It ties together mount, AIL, CIL, target device, workqueues, operational state, recovered intents, iclog geometry, log geometry, iclog ring state, atomic tail LSN, grant heads, sysfs object, recovery LSN, and iclog roundoff.

## State and Flags

The iclog state enum covers active, want-sync, syncing, done-sync, callback, and dirty states. Flags include `XLOG_ICL_NEED_FLUSH` and `XLOG_ICL_NEED_FUA`.

Ticket flags include `XLOG_TIC_PERM_RESERV`.

Covering states model idle log cover progression: idle, need, done, need2, done2. These support the two-dummy-transaction scheme used to make allocation transactions safe after idle periods.

Operational state bits include active recovery, recovery needed, log I/O error, tail warning issued, and shutdown started.

CIL flags include `XLOG_CIL_EMPTY` and `XLOG_CIL_PCP_SPACE`.

## Thresholds and Accounting

`XLOG_CIL_SPACE_LIMIT` computes the background CIL push threshold as the smaller of one-eighth of log size and sixteen times the iclog buffer window. `XLOG_CIL_BLOCKING_SPACE_LIMIT` doubles that threshold for throttling.

The extensive comments explain why CIL checkpoint sizing is based on consumed space rather than number of vectors, why dynamic reservation stealing avoids grant-head deadlocks, and why memory pinning imposes a physical upper bound.

`struct xlog_grant_head` contains the grant lock, waiter list, and atomic grant byte count for reservation and write heads.

## Helper Functions

- `xlog_get_client_id` extracts a client id from packed op header bytes.
- `xlog_recovery_needed`, `xlog_in_recovery`, and `xlog_is_shutdown` query operation state bits.
- `xlog_shutdown_wait` waits until shutdown state is visible.
- `xlog_crack_atomic_lsn` and `xlog_assign_atomic_lsn` safely read/write atomic LSNs.
- `xlog_wait` wraps serialized waitqueue sleeps used by log code.
- `xlog_lsn_sub` computes byte distance between two LSNs, handling single-cycle wrap.
- `xlog_valid_lsn` checks whether a metadata LSN is behind the current log head, with a lockless fast path and locked recheck for wrap races.
- `xlog_kvmalloc` open-codes kmalloc/vmalloc fallback to avoid expensive direct reclaim behavior.
- `xlog_item_space` calculates log space for iovec payload plus op headers.
- `xlog_cycle_data` locates cycle-data storage in the main or extended log record header.

## Internal Prototypes

The header declares recovery entry points, checksum support, ticket allocation, transaction/ticket debug printing, log write functions, ticket grant helpers, iclog state functions, CIL initialization/destruction/commit/force routines, and grant-space return.

## Research Notes

This header captures the design constraints of the log subsystem: hot-path cacheline placement, waitqueue serialization, atomic LSN sampling, dynamic CIL reservation stealing, bounded CIL memory pressure, and careful log wrap handling. It is essential context for understanding both `xfs_log.c` and `xfs_log_cil.c`.
