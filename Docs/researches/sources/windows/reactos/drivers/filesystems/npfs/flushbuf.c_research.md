# File Research: sources/windows/reactos/drivers/filesystems/npfs/flushbuf.c

## Purpose
Implements `IRP_MJ_FLUSH_BUFFERS` for named pipes.

## Main Responsibilities
- `NpCommonFlushBuffers`:
  - Decodes the file object and validates it is a CCB.
  - Locks the nonpaged CCB resource.
  - Selects the opposite-direction write queue for the current pipe end.
  - If the queue contains write entries, inserts a special queue entry of type `2` with zero data size so the flush can pend behind existing writes.
  - Otherwise completes immediately with success.
- `NpFsdFlushBuffers`:
  - Wraps the common helper in filesystem entry/exit and shared VCB locking.
  - Completes the IRP unless the operation pended.

## Important Interactions
- Special queue entry type `2` is handled by `datasup.c` as a non-real queue entry that can later be skipped/completed by `NpGetNextRealDataQueueEntry`.
- Flush behavior depends on the write queue draining through reads.

## Risks / Review Notes
- The special entry type is not named in the enum, so behavior is implicit across `flushbuf.c` and `datasup.c`.
- Flush does not force delivery; it waits only when existing write entries are queued.
