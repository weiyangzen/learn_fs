# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/jbd.h

This is the main Linux JBD journaling header adapted for ReactOS/Ext2Fsd.

Major content:
- JBD includes and compatibility hooks.
- `jbdlock_t` mapped to `FAST_MUTEX`, with init/lock/unlock/assert helpers.
- JBD debug, allocation, and free helpers.
- Opaque `handle_t` and `journal_t` typedefs.
- On-disk journal structures: descriptor types, `journal_header_t`, `journal_block_tag_t`, `journal_revoke_header_t`, `journal_superblock_t`.
- Journal feature-test macros and known feature masks.
- Buffer state bits for JBD integration, buffer flag helper macro invocations, and `jh2bh`/`bh2jh`.
- Bit-spinlock wrappers for buffer state and journal-head locking.
- Concrete `struct handle_s`, `struct transaction_s`, and `struct journal_s`.
- Journal flags such as `JFS_UNMOUNT`, `JFS_ABORT`, `JFS_ACK_ERR`, `JFS_FLUSHED`, `JFS_LOADED`, `JFS_BARRIER`.
- Prototypes for buffer filing, log buffer allocation, commit/checkpoint management, metadata buffer writeout, wait/lock operations, handle lifecycle, journal start/restart/extend/access/dirty/forget/stop/flush/recovery/destroy/abort/error handling, journal-head management, revoke support, log thread control, checkpointing, and tail cleanup.
- Transaction ID comparison helpers `tid_gt` and `tid_geq`.
- Journal buffer list type constants `BJ_*`.

Role:
- Supplies the journaling state machine API and structures needed by ext3 recovery and metadata journaling in the driver.

Notable ReactOS adaptation:
- `journal_current_handle()` is stubbed to return `NULL`.
- Locking uses Windows fast mutexes instead of Linux spinlocks/semaphores for many journal locks.
- `jbd_ENOSYS()` retains Linux-style sleep/schedule behavior and depends on task-state compatibility definitions.

Notable risk:
- This header describes rich Linux JBD semantics; any stubbed compatibility primitive can weaken transaction, checkpoint, or abort behavior if callers assume full Linux behavior.
