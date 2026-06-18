# File Research: sources/windows/reactos/drivers/filesystems/npfs/write.c

## Purpose
Implements normal and fast write handling for named pipes.

## Main Responsibilities
- `NpCommonWrite`:
  - Decodes file object and validates CCB state.
  - Rejects invalid write direction based on pipe configuration.
  - Selects outbound or inbound queue based on pipe end.
  - Checks available quota and completion mode.
  - Calls `NpWriteDataQueue` to satisfy queued readers.
  - If not all data can be delivered, queues remaining data as a buffered write entry.
  - Signals event buffer when present.
- `NpFsdWrite`:
  - Uses shared VCB lock.
  - Completes IRP unless pending.
- `NpFastWrite`:
  - Calls common write without an IRP.
  - Returns false when synchronous fast I/O cannot complete.

## Important Interactions
- Write delivery is implemented in `writesup.c`.
- Pending write queue entries are managed by `datasup.c`.
- Read mode on the receiving end determines message/byte completion behavior.
- Client security context capture happens in data queue support.

## Risks / Review Notes
- Complete-operation mode for message pipes can return success with zero bytes written when quota is insufficient.
- Fast write has no IRP to pend, so quota limits can force fallback.
