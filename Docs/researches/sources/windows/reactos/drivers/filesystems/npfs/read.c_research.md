# File Research: sources/windows/reactos/drivers/filesystems/npfs/read.c

## Purpose
Implements normal and fast read handling for named pipes.

## Main Responsibilities
- `NpCommonRead`:
  - Decodes the file object and validates CCB state.
  - Rejects invalid read direction based on pipe configuration.
  - Selects inbound or outbound queue based on pipe end.
  - If queued writes exist, drains them through `NpReadDataQueue`.
  - If pipe is closing, returns `STATUS_PIPE_BROKEN`.
  - If complete-operation mode and no data, returns `STATUS_PIPE_EMPTY`.
  - Otherwise queues the read IRP as a `ReadEntries` buffered entry.
  - Signals assigned event buffer when present.
- `NpFsdRead`:
  - Uses shared VCB lock.
  - Completes the IRP unless pending.
- `NpFastRead`:
  - Calls `NpCommonRead` without an IRP.
  - Returns `FALSE` when the fast path cannot complete synchronously.

## Important Interactions
- Uses `NpDecodeFileObject`, per-CCB nonpaged resource lock, and `NpReadDataQueue`.
- Queued reads are later satisfied by `writesup.c`.
- Fast-read counters track true/false results.

## Risks / Review Notes
- Fast read cannot pend; if data is unavailable and the operation would need queuing, it returns false for fallback.
- Event-buffer signaling is present but event assignment/query support is unimplemented in `fsctrl.c`/`strucsup.c`.
