# File Research: sources/windows/dokany/sys/write.c

## Purpose
Implements Dokany write IRP dispatch and completion, bridging kernel write requests to user-mode filesystem callbacks while handling cache, oplock, paging I/O, large payload, and file-size update concerns.

## Main Behavior
- `DokanDispatchWrite()` logs write parameters, immediately succeeds zero-length writes, validates file object/VCB/CCB, and rejects directory writes.
- Resolves the write buffer from an MDL via `MmGetSystemAddressForMdlNormalSafe()` or from `Irp->UserBuffer`.
- Detects write-to-end-of-file, paging I/O, noncached I/O, and synchronous I/O flags.
- For non-paging writes with a data section, flushes and purges cache around the write range, using Dokany paging I/O locks.
- Rejects paging I/O write-to-EOF as a no-op success because paging writes require concrete offsets.
- Builds an `EVENT_CONTEXT` containing write metadata, file name, and copied write bytes. It guards event length with a 64-bit calculation to avoid overflow.
- For normal-size events, performs oplock checks and registers the full event context as a pending IRP.
- For large writes exceeding `EVENT_CONTEXT_MAX_SIZE`, stores the full event context in `DriverContext[DRIVER_CONTEXT_EVENT]`, sends a smaller request containing metadata and requested full length, and lets later event retrieval copy the larger context.
- Marks event flags for paging, synchronous, noncached, and write-to-EOF cases; resolves `FILE_USE_FILE_POINTER_POSITION` against `FileObject->CurrentByteOffset` for synchronous I/O.
- `DokanCompleteWrite()` propagates user context, status, and written byte count; on success it updates file size when the reported current byte offset grows, reports size change notifications, marks last-write change, sets `FO_FILE_MODIFIED` for non-paging writes, and advances `CurrentByteOffset` for synchronous non-paging writes.

## Integration Points
- Dispatched from `dispatch.c` for `IRP_MJ_WRITE` and completed from `event.c`.
- Consumed by user-mode write handling in `sources/windows/dokany/dokan/write.c`, including the large-write `RequestLength` path.
- Uses FCB/CCB helpers, oplock helpers, cache manager APIs, paging I/O locks, event allocation/registration, and notification reporting.
- Shares large-event cleanup and retrieval behavior with `event.c` via `DRIVER_CONTEXT_EVENT`.

## Risks and Notes
- The function copies the entire write payload into nonpaged/event memory before handing it to user mode; the large-write path mitigates event queue size but still stores a full kernel-side event context.
- Correct cleanup depends on `DriverContext[DRIVER_CONTEXT_EVENT]` being cleared or freed by the event path for oversized writes.
- Cache flush/purge before user-mode completion is important for coherency with mapped sections and should be treated carefully.
- Oplock checks differ slightly between normal and large paths: normal path uses `DokanCheckOplock`, while the large path calls `FsRtlCheckOplock` directly.
- Completion trusts user-mode `EventInfo->Operation.Write.CurrentByteOffset` for file size and current offset updates.
