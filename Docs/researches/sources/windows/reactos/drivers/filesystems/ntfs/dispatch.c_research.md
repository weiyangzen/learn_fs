# File Research: sources/windows/reactos/drivers/filesystems/ntfs/dispatch.c

Read status: complete file, 206 lines.

This file is the central IRP dispatcher and queue bridge for the NTFS FSD.

Key entry points:
- `NtfsFsdDispatch()` allocates an NTFS IRP context and calls `NtfsDispatch()`, completing immediately with insufficient resources if allocation fails.
- `NtfsDispatch()` enters filesystem context, marks top-level IRP state, switches on major function, calls the matching NTFS handler, completes the IRP when `IRPCONTEXT_COMPLETE` is set, queues when `IRPCONTEXT_QUEUE` is set, frees the IRP context otherwise, clears the top-level IRP, and exits filesystem context.
- `NtfsQueueRequest()` marks the IRP pending, sets can-wait, initializes a work item, and queues it to `CriticalWorkQueue`.
- `NtfsDoRequest()` runs queued work and re-enters `NtfsDispatch()`.

Important dependencies:
- All major operation handlers: create, close, cleanup, read, write, query/set file info, query/set volume info, directory control, device control, filesystem control.
- Global write gate for `IRP_MJ_WRITE` and `IRP_MJ_SET_INFORMATION`.
- Lookaside allocation/free for IRP contexts.

Notable behavior:
- Write and set-information requests are denied unless experimental write support is enabled.
- Unsupported major functions fall through with initial `STATUS_UNSUCCESSFUL`.
- The assertion before completion/queueing documents the intended mutually valid flag states.
