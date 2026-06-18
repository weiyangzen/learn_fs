# File Research: sources/windows/dokany/sys/read.c

Implements `IRP_MJ_READ` dispatch and completion.

Key entry points:
- `DokanDispatchRead()` validates read requests, handles special recognizer/complete cases, creates MDLs when needed, checks cache/oplocks/byte-range locks, builds `READ_CONTEXT`, and registers the pending IRP.
- `DokanCompleteRead()` maps the target buffer, copies user-mode data into it, updates synchronous current byte offset, sets status/information, and frees Dokan-allocated MDLs.

Core mechanics:
- Zero-length reads complete immediately.
- `IRP_MN_COMPLETE` clears `MdlAddress` and succeeds.
- File-system recognizer reads with no `FileObject` but an MDL are treated as successful and report the requested length.
- `FILE_USE_FILE_POINTER_POSITION` uses `FileObject->CurrentByteOffset`; otherwise the IRP byte offset is used.
- If the IRP has no MDL, Dokan allocates one so completion can occur in another thread context.
- Directories reject reads.
- Paging, synchronous, and no-cache state is reflected into event file flags.
- Non-paging reads flush cache for existing data sections before dispatch, then perform oplock and byte-range lock checks.
- Completion copies `EventInfo->Buffer` to the MDL or user buffer and updates `FO_SYNCHRONOUS_IO` current byte offset only for successful non-paging reads with data.

Important invariants:
- Read buffer length must be at least the returned user-mode buffer length.
- FCB filename is read under FCB lock while building the event.
- Oplock failure frees the event context unless the IRP has been posted pending.
- Dokan frees only MDLs it allocated, tracked by `DOKAN_MDL_ALLOCATED`.

Filesystem relevance:
- This is Dokan's main data-read path from Windows callers to user-mode filesystem implementation and back into the original IRP buffer.

Notable risks:
- Completion trusts user mode's returned current byte offset for synchronous reads.
- Recognizer reads are stubbed as success rather than returning real boot-sector data.
- Cache flush before non-paging read is conservative and may affect performance.
