# File Research: sources/windows/reactos/drivers/filesystems/msfs/rw.c

This file implements MSFS read and write behavior.

`MsfsRead` is server-side only. If messages are queued, it removes the oldest message, copies up to the caller’s requested length into the target buffer, frees the message, and completes successfully. If no messages are queued, a zero timeout completes immediately with `STATUS_IO_TIMEOUT`; otherwise it allocates a DPC context, inserts the IRP into the cancel-safe queue, starts a timer unless the timeout is infinite, marks the IRP pending, and returns `STATUS_PENDING`.

`MsfsWrite` is client-side only. It copies the caller buffer into a newly allocated message, appends it to the mailslot queue, then removes one pending read IRP if present. For a pending reader, it cancels or synchronizes with the timeout timer, frees the context, and calls `MsfsRead` again to satisfy the read from the newly queued message.

Research notes:
- Server handles cannot write, and client handles cannot read.
- Reads copy `min(Message->Size, Length)` but set `IoStatus.Information` to the full message size.
- The driver supports MDL-backed direct I/O and falls back to `UserBuffer`.
- Message size limits are stored in the FCB but not enforced in this write path.
