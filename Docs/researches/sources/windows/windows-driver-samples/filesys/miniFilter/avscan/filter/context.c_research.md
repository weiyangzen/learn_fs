# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.c

Filter Manager context implementation for stream, stream-handle, transaction, section, and instance contexts, plus manual allocation/refcounting for scan contexts. It registers all minifilter context types and owns cleanup for auxiliary allocations inside those contexts.

Key responsibilities:
- `ContextRegistration` registers stream, stream-handle, transaction, section, and instance contexts with Filter Manager.
- `AvCreateStreamContext` allocates a stream context, allocates a nonpaged scan synchronization event, initializes the event signaled, and marks both normal and transaction state as modified.
- `AvCreateStreamHandleContext` allocates a small per-handle context used primarily for prefetch tracking.
- `AvFindOrCreateTransactionContext` retrieves or allocates a transaction context, references the KTM transaction object, initializes its resource/list, and sets the Filter Manager transaction context.
- `AvCreateSectionContext` allocates a section context and records current file size when available.
- `AvEnumerateInstances` and `AvFreeInstances` enumerate all instances for volume-to-instance lookup in the communication path.
- `AvAllocateScanContext`, `AvReferenceScanContext`, and `AvReleaseScanContext` manage non-Filter-Manager scan contexts with an interlocked refcount, instance reference, and file-object reference.

Cleanup behavior:
- `AvStreamContextCleanup` asserts the stream is no longer linked to a transaction context and frees its scan synchronization event.
- `AvTransactionContextCleanup` deletes/frees its resource and dereferences the transaction object.
- `AvSectionContextCleanup` asserts section handle/object have already been cleared.
- `AvInstanceContextCleanup` asserts the file-state cache is empty and deletes the instance resource when the filesystem supports caching.

Dependencies:
- Filter Manager context APIs, KTM transaction objects, `ERESOURCE`, stream/transaction structures from `context.h`, scan context structure from `avscan.h`, and allocation wrappers from `utility.h`.

Research notes:
- Transaction context resources are separately allocated from nonpaged pool because `ERESOURCE` cannot live in paged memory.
- Scan contexts are not Filter Manager contexts; they are pool allocations tracked by the AV driver and global scan list.
- `AvReleaseScanContext` comments note the simple refcount assumes references/releases are not raced beyond intended usage.
