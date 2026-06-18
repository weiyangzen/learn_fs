# File Research: sources/windows/reactos/drivers/filesystems/msfs/msfssup.c

This file implements support routines for the MSFS cancel-safe queue and read timeout handling.

Cancel-safe queue callbacks:
- `MsfsInsertIrp`: appends an IRP to the FCB pending queue.
- `MsfsRemoveIrp`: removes an IRP from that queue.
- `MsfsPeekNextIrp`: returns the next pending IRP, optionally filtered by file object.
- `MsfsAcquireLock` / `MsfsReleaseLock`: protect the queue with `Fcb->QueueLock`.
- `MsfsCompleteCanceledIrp`: completes canceled IRPs with `STATUS_CANCELLED`.

`MsfsTimeout` runs as a DPC, removes the timed-out IRP from the cancel-safe queue, completes it with `STATUS_IO_TIMEOUT`, and frees its context. If the IRP was already removed by a writer, it signals the event so the writer can safely free the context.

Research notes:
- Timeout handling explicitly manages the race between timer DPC and writer wake-up.
- The DPC context is allocated per pending read in `rw.c`.
- Canceled IRPs report zero information.
