# File Research: sources/os/linux/linux/fs/xfs/xfs_log_priv.h

## Purpose

`xfs_log_priv.h` defines the private data structures, state constants, helper functions, and internal prototypes shared by XFS log manager, CIL, and recovery code. It is the structural contract for in-core log buffers, checkpoint contexts, CIL state, grant heads, log geometry/state, ticket accounting, LSN helpers, allocation helpers, and log item space calculations.

## Core Structures

### `struct xfs_log_iovec`

Represents one formatted log region with an address, byte length, and region type. Region type values come from `xfs_log.h`.

### `struct xfs_log_vec`

Represents the formatted log-vector state for one log item:

- list linkage for CIL chains
- ordering id
- iovec count and iovec array
- owning log item
- formatted buffer pointer
- accounted bytes, used bytes, and allocation size

The CIL swaps these between active item state and shadow buffers during relogging.

### `struct xlog_ticket`

Tracks reservation ownership:

- grant wait queue node and owning task
- transaction id
- reference count
- current and unit reservations
- original/current reservation counts
- permanent-reservation flag
- number of iclog headers included in the reservation

Tickets are used both by ordinary transactions and by CIL checkpoint contexts.

### `struct xlog_in_core`

Represents one in-core log buffer in the iclog ring:

- force/write wait queues
- ring links
- owning log pointer
- usable size, offset, state, flags, data pointer
- callback list for completed CIL contexts
- cacheline-separated reference count
- log record header pointer
- debug CRC failure bit
- semaphore used to serialize IO completion against teardown
- end-IO work item
- embedded bio and flexible bio_vec array

The comments emphasize cacheline separation for fields contended by independent CPUs.

### `struct xfs_cil_ctx`

Tracks one checkpoint context:

- owning CIL and sequence
- start and commit LSNs
- commit iclog reference
- checkpoint ticket
- aggregate space count
- busy extents
- log items and log-vector chain
- iclog callback entry
- committing-list linkage
- push work
- item ordering counter
- CPU mask identifying per-CPU CIL data touched by this context

### `struct xlog_cil_pcp`

Per-CPU CIL staging area containing space-used/reserved counters plus busy extent and log item lists.

### `struct xfs_cil`

Global CIL state for one log:

- owning log
- flags and iclog-header counter
- push workqueue
- context rwsem and active context
- push lock, push sequence, stable-commit request flag
- committing context list and wait queues
- current sequence and push-throttle wait queue
- per-CPU state pointer

The structure is cacheline aligned because it sits in hot transaction commit paths.

### `struct xlog_grant_head`

Represents either the reservation or write grant head with its own cacheline-aligned lock, waiter list, and atomic grant-space counter.

### `struct xlog`

Main in-core log object containing:

- mount, AIL, CIL, buftarg, and IO completion workqueue pointers
- background work, opstate bits, quotaoff flags, recovery cancel table, recovered deferred ops
- iclog geometry and physical log geometry
- iclog ring state protected by `l_icloglock`
- current/previous log cycle and block
- atomic tail LSN on a separate cacheline
- reservation and write grant heads
- tail-space accounting
- sysfs kobject
- recovery LSN tracking
- iclog roundoff

## State and Flag Definitions

Iclog states:

- `XLOG_STATE_ACTIVE`
- `XLOG_STATE_WANT_SYNC`
- `XLOG_STATE_SYNCING`
- `XLOG_STATE_DONE_SYNC`
- `XLOG_STATE_CALLBACK`
- `XLOG_STATE_DIRTY`

Iclog flags:

- `XLOG_ICL_NEED_FLUSH`
- `XLOG_ICL_NEED_FUA`

Ticket flags:

- `XLOG_TIC_PERM_RESERV`

Cover states:

- `XLOG_STATE_COVER_IDLE`
- `XLOG_STATE_COVER_NEED`
- `XLOG_STATE_COVER_DONE`
- `XLOG_STATE_COVER_NEED2`
- `XLOG_STATE_COVER_DONE2`

Log opstate bits:

- `XLOG_ACTIVE_RECOVERY`
- `XLOG_RECOVERY_NEEDED`
- `XLOG_IO_ERROR`
- `XLOG_TAIL_WARN`
- `XLOG_SHUTDOWN_STARTED`

CIL flags:

- `XLOG_CIL_EMPTY`
- `XLOG_CIL_PCP_SPACE`

## CIL Limit Macros

`XLOG_CIL_SPACE_LIMIT(log)` chooses the smaller of one-eighth of the log and 16 times the total iclog record window. `XLOG_CIL_BLOCKING_SPACE_LIMIT(log)` doubles that value. The long comment explains the tradeoff: keep checkpoints below recovery/log-reservation size constraints while bounding pinned metadata memory and retaining relogging efficiency.

## Internal API Declarations

Recovery:

- `xlog_recover()`
- `xlog_recover_finish()`
- `xlog_recover_cancel()`

Log writing and ticket internals:

- `xlog_cksum()`
- `xlog_ticket_alloc()`
- `xlog_print_tic_res()`
- `xlog_print_trans()`
- `xlog_write()`
- `xlog_write_one_vec()`
- `xfs_log_ticket_ungrant()`
- `xfs_log_ticket_regrant()`
- `xlog_state_switch_iclogs()`
- `xlog_state_release_iclog()`

CIL:

- `xlog_cil_init()`
- `xlog_cil_init_post_recovery()`
- `xlog_cil_destroy()`
- `xlog_cil_empty()`
- `xlog_cil_commit()`
- `xlog_cil_set_ctx_write_state()`
- `xlog_cil_flush()`
- `xlog_cil_force_seq()`
- inline `xlog_cil_force()`

Wait and iclog force support:

- inline `xlog_wait()`
- `xlog_wait_on_iclog()`

Grant/tail support:

- `xlog_lsn_sub()`
- `xlog_grant_return_space()`

## Inline Helpers

- `xlog_get_client_id()` extracts the client id from a packed big-endian opheader word; the comment notes historic endian awkwardness in packed log recovery handling.
- `xlog_recovery_needed()`, `xlog_in_recovery()`, and `xlog_is_shutdown()` test log opstate bits.
- `xlog_shutdown_wait()` waits until shutdown state is visible.
- `xlog_crack_atomic_lsn()` samples an atomic LSN once and splits it into cycle/block.
- `xlog_assign_atomic_lsn()` stores an LSN constructed from cycle/block.
- `xlog_wait()` implements the log code’s spinlock-serialized exclusive wait pattern.
- `xlog_lsn_sub()` computes byte distance between two LSNs, handling single-cycle wrap and allowing shutdown exceptions.
- `xlog_valid_lsn()` performs mostly lockless validation that a metadata LSN is not ahead of the current log head, with a locked recheck for wrap races.
- `xlog_kvmalloc()` open-codes kmalloc-with-vmalloc-fallback using no-direct-reclaim flags, relying on caller NOFS context.
- `xlog_item_space()` computes log space for item payload bytes plus per-iovec opheader/alignment overhead.
- `xlog_cycle_data()` returns the cycle-data slot for a 512-byte block, including v2 extended headers after the original header’s array is exhausted.

## Important Design Notes Captured in Comments

- Log covering requires two dummy transactions to ensure recovery starts beyond the last potentially replayable allocation transaction.
- CIL reservation strategy avoids static checkpoint reservations because regranting during push can deadlock. Instead, transaction commits transfer unused reservation into the checkpoint context.
- CIL size limits balance log-space safety, latency, and pinned-memory footprint.
- `l_tail_lsn`, grant heads, and some iclog fields are cacheline-separated because they are hot under concurrent transaction workloads.
- `xlog_valid_lsn()` depends on write/read memory ordering between current block and current cycle updates during log wrap.
- `xlog_kvmalloc()` avoids expensive direct reclaim in log-vector allocation paths.

## Research Notes

This private header is the best compact map of XFS logging internals. It shows that the implementation is organized around three shared objects: `xlog` for physical log/iclog state, `xfs_cil` for delayed checkpoint aggregation, and `xlog_ticket` for reservation accounting. It also documents many of the hidden constraints that drive the C files: recovery ordering, log cover semantics, checkpoint size thresholds, cacheline contention, and lockless LSN validation.
