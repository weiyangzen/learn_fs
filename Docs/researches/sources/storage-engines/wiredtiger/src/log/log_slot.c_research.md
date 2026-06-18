# sources/storage-engines/wiredtiger/src/log/log_slot.c

## Purpose
Implements WiredTiger's consolidated logging slot pool. Threads join an active `WTI_LOGSLOT`, reserve space for their log record, copy or write their portion, and release it so the log writer can flush a larger combined buffer instead of many small writes.

## Important APIs, Types, and Functions
Key public/internal entry points are `__wti_log_slot_init`, `__wti_log_slot_destroy`, `__wti_log_slot_join`, `__wti_log_slot_release`, `__wti_log_slot_switch`, `__wti_log_slot_activate`, and `__wti_log_slot_free`. The core types are `WTI_LOG`, `WTI_LOGSLOT`, and `WTI_MYSLOT`; slot state encodes joined bytes, released bytes, close/unbuffered/reserved flags, and is manipulated with atomic macros from `log_private.h`.

## Control Flow
Initialization marks every pool entry free, allocates buffers, activates slot 0, and installs it as `log->active_slot`. Writers call `__wti_log_slot_join`, loop on the active slot until they can atomically add their record size, then return the slot pointer and offsets. Oversized records or diagnostic forcing mark the join as unbuffered. `__wti_log_slot_release` advances `slot_last_offset` and atomically adds the released size. Slot switching takes the slot lock, closes the current active slot, installs a new free slot, and releases the old slot to the write path when every joined writer has released.

## State and Persistence Behavior
Slot state is in memory, but it controls persistent log file offsets and write ordering. Closing a slot computes `slot_end_lsn` from buffered and unbuffered sizes, advances `log->alloc_lsn`, and may schedule dirty-log or explicit sync flags on the slot. Destroy writes any unreleased buffered bytes before freeing buffers. Release LSNs and file handles bridge slot switching across log file rotation.

## Dependencies and Integration Points
The file depends on `wt_internal.h`, `log_private.h`, LSN helpers, log allocation/release/fill routines, stats counters, slot spinlock macros, condition variables, and connection panic handling. It integrates with `log_write.c` style callers that join/fill/release slots and with the write-LSN worker that drains closed slots.

## Risks and Edge Cases
The state word is concurrency-critical: stale slot pointers, CAS races, unbuffered handoff, and forced switching all depend on exact flag ordering. `__log_slot_close` waits for unbuffered size publication and aborts under slow-operation diagnostics if it appears stuck. `__log_slot_new` can spin if all slots are reserved and must release the slot lock to let the writer progress. Forced switches return `EBUSY` if writers are in progress. Buffer sizing is capped to one tenth of the log file maximum to avoid aggressive rotations.

## Test Signals
Useful signals are stress tests with many concurrent log writers, log file rotation, forced fsync/dsync/flush paths, oversized log records, incremental backup/system records, crash recovery, and diagnostic builds that exercise timeout dumps. Counters such as `log_slot_races`, `log_slot_yield`, `log_slot_no_free_slots`, `log_slot_unbuffered`, and `log_slot_switch_busy` indicate slot behavior under load.
