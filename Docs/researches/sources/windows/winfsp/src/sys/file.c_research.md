# File Research: sources/windows/winfsp/src/sys/file.c

## Role

Core WinFsp file-node and file-description implementation. This file manages the kernel in-memory representation of opened filesystem objects: lifetime, context-table membership, share access, ERESOURCE locking, cache metadata, named stream coordination, cleanup/close, rename propagation, notifications, byte-range locks, and helper opens of main files.

## Main Structures And State

The central object is `FSP_FILE_NODE`, stored in `FILE_OBJECT->FsContext` elsewhere in the driver. It owns or references:

- `FSRTL_ADVANCED_FCB_HEADER Header`, with file sizes, section object pointers, and main/paging resources.
- `FSP_FILE_NODE_NONPAGED`, allocated separately for resources, fast mutex, spin lock, section pointers, and nonpaged metadata-cache handles.
- Context-table entries keyed both by user context and by file name.
- Share-access counters and extra WinFsp counters: `ActiveCount`, `OpenCount`, `HandleCount`, delete-pending state, stream delete-denial counters, POSIX-delete state, and cache change numbers.
- Cached basic/file info plus cached security, directory, stream, and EA blobs in volume-level `FspMetaCache` instances.

`FSP_FILE_DESC`, stored in `FILE_OBJECT->FsContext2`, tracks per-handle state such as granted access, user context2, directory enumeration pattern/marker, delete-on-close/POSIX delete, disposition retry status, metadata flags, and optional main-file handle/object.

## Important Entry Points

- `FspFileNodeCreate` / `FspFileNodeDelete`: allocate and tear down file nodes, resources, file locks, oplocks, per-stream contexts, volume references, and metadata-cache entries.
- `FspFileNodeAcquire*F`, `TryAcquire*F`, `Release*F`, `ReleaseOwner*F`: wrapper layer around main and paging I/O ERESOURCE acquisition, with top-level IRP flag tracking to assert lock state.
- `FspFileNodeOpen`: inserts or finds a node in the volume name table, enforces delete-pending and share-access rules, handles main-file/named-stream delete sharing behavior, and bumps active/open/handle counts.
- `FspFileNodeCleanup`, `CleanupFlush`, `CleanupComplete`, `Close`: drive delete-on-close, POSIX delete, cache uninitialization, context-table removal, share-access removal, count decrements, and final dereference.
- `FspFileNodeFlushAndPurgeCache`: wraps cache manager flush/purge paths, using `CcCoherencyFlushAndPurgeCache` when available and falling back to `CcFlushCache`/`CcPurgeCacheSection`.
- `FspFileNodeOverwriteStreams`, `CheckBatchOplocksOnAllStreams`, `RenameCheck`, `Rename`: handle named stream invalidation and recursive rename behavior across descendants.
- `FspFileNodeGet/TryGet/Set/TrySet/InvalidateFileInfo`: maintain cached WinFsp file info and synchronize Cc file sizes.
- `FspFileNodeReference/Set/TrySet/InvalidateSecurity`, `DirInfo`, `StreamInfo`, `Ea`: per-node metadata-cache handles protected by the node lock and, for invalidation races, `NpInfoSpinLock`.
- `FspFileNodeNotifyChange` and `FspFileNodeInvalidateCachesAndNotifyChangeByName`: translate file vs stream notifications, invalidate relevant caches, and report changes.
- `FspFileNodeProcessLockIrp`: delegates byte-range locking to `FsRtlProcessFileLock`.
- `FspFileDescCreate/Delete/ResetDirectory/SetDirectoryMarker`: handle per-open directory enumeration state.
- `FspMainFileOpen/Close`: opens the main file for stream operations using an ECP GUID and `IoCreateFileEx`.
- `FspFileNodeOplockPrepare/Complete`: support oplock break work-item handoff.

## Control Flow And Algorithms

The file-node open path first locks the volume context table. It may insert the new node or reuse an existing node with the same name. It performs special named-stream vs main-file sharing checks, checks delete-pending, asks the I/O manager share-access routines to validate or update `ShareAccess`, and then increments WinFsp’s own active/open/handle counters. On first active use it links the node into the volume active list.

Cleanup is split into decision, optional flush, and completion phases. `FspFileNodeCleanup` computes whether delete or truncate-on-close should happen. `FspFileNodeCleanupComplete` removes share access, possibly deletes the file node from the name table, propagates deletion to open stream nodes, updates file sizes for delete/truncate, resets truncate-on-close, calls `CcUninitializeCacheMap`, and dereferences nodes removed from the context table.

Rename is descendant-aware. `GATHER_DESCENDANTS` enumerates name-table entries under a prefix, optionally references them, and grows from a 16-entry stack array to heap allocation when needed. `FspFileNodeRenameCheck` blocks unsafe renames: it checks replaced targets, image sections, cleaned-up-but-open mapped files, descendant handles, POSIX rename exceptions, and batch/handle oplocks. `FspFileNodeRename` then removes each descendant from the name table, rewrites its file name by replacing the old prefix with the new one, reinserts it, and handles collisions with replaced open nodes.

Metadata caching uses volume-level meta caches. File info has expiration timestamps and change numbers; security/dir/stream/EA caches store opaque buffers by cache item id in `NonPaged`. Try-set functions compare the saved change number from request preparation to detect intervening mutations before accepting a user-mode response.

## Concurrency And Locking

The main synchronization layers are:

- Volume context-table lock for name/context lists and open/handle counters.
- `Header.Resource` for main file-node state.
- `Header.PagingIoResource` for paging I/O coordination.
- Volume rename resource, held externally during rename operations.
- `NpInfoSpinLock` for cache-handle invalidation races against setters.
- FSRTL file locks and oplocks.

Lock wrappers normalize stream nodes to their main file when needed and store lock flags in the current top-level IRP. Owner-based release is used for IRPs posted to user mode, allowing request finalizers to release locks even on cancellation or retry.

## Integration Points

This file is foundational for `create.c`, `cleanup.c`, `dirctl.c`, `fileinfo.c`, `flush.c`, `fsctl.c`, `read.c`, `write.c`, and `security.c`. It depends heavily on helpers from the WinFsp sys layer: context-table APIs, IOQ/request APIs, Cc wrappers, notify helpers, file-name helpers, meta-cache helpers, and volume parameters.

## Edge Cases And Risks

- Many behaviors intentionally emulate NTFS/FastFat and are documented as experimentally derived, especially main-file/named-stream share violations and POSIX rename behavior.
- Rename completion can block by design, which is unusual for IRP completion paths but documented here as intentional.
- `FspFileNodeSetFileInfo` has a complex recovery path when `CcSetFileSizes` fails; it flushes, purges, uninitializes cache maps, and waits for cache teardown while holding the file-node lock.
- Metadata invalidation invalidates cache items but does not always clear the stored item id; correctness relies on meta-cache semantics and reference failures after invalidation.
- The descendant macros store low-bit flags in file-node pointers, relying on pointer alignment.
