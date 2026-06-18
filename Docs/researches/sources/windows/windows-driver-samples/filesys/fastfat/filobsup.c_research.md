# File Research: sources/windows/windows-driver-samples/filesys/fastfat/filobsup.c

## Role

`filobsup.c` implements FastFAT file-object support. It binds Windows `FILE_OBJECT` instances to FastFAT VCB/FCB/DCB/CCB structures, decodes those bindings back into open types, and provides cache/section purge helpers used by rename, flush, teardown, and invalidation paths.

## File Object Setup

`FatSetFileObject` writes filesystem-private pointers into a `FILE_OBJECT`.

It supports these open shapes:

- `UnopenedFileObject`
- `UserFileOpen`: FCB plus CCB
- `EaFile`: FCB without CCB
- `UserDirectoryOpen`: DCB/root DCB plus CCB
- `UserVolumeOpen`: VCB plus CCB
- `VirtualVolumeFile`: VCB without CCB
- `DirectoryFile`: DCB/root DCB without CCB

The routine asserts type consistency rather than dynamically recovering from invalid combinations. When the object is attached to an FCB/DCB, it sets `FileObject->Vpb` from the owning VCB. If the FCB is temporary, it also sets `FO_TEMPORARY_FILE`. Finally it stores:

- `FileObject->FsContext = VcbOrFcbOrDcb`
- `FileObject->FsContext2 = Ccb`

## File Object Decode

`FatDecodeFileObject` reverses the binding and returns `TYPE_OF_OPEN`.

Behavior by `FsContext` node type:

- `NULL`: returns `UnopenedFileObject`; all outputs are null.
- `FAT_NTC_VCB`: returns `VirtualVolumeFile` if no CCB, otherwise `UserVolumeOpen`.
- `FAT_NTC_ROOT_DCB` or `FAT_NTC_DCB`: returns `DirectoryFile` if no CCB, otherwise `UserDirectoryOpen`.
- `FAT_NTC_FCB`: returns `UserFileOpen` when a CCB exists; otherwise returns `EaFile` only if the FCB is the VCB EA FCB.
- Unknown or inconsistent types bugcheck.

This routine is a key dependency for dispatch paths in `fileinfo.c` and `flush.c`.

## Purging Referenced File Objects

`FatPurgeReferencedFileObjects` walks a subtree non-recursively starting at an FCB/DCB and tries to force Cache Manager or Memory Manager to drop referenced file objects and sections.

Key behavior:

- Requires wait-capable IRP context.
- Forces delayed closes first with `FatFspClose`.
- Uses top-down enumeration with `FatGetNextFcbTopDown`.
- Computes the next node before acting on the current node, because purging can cause the current node and ancestors to disappear.
- Skips volume-label style entries marked `FAT_DIRENT_ATTR_VOLUME_ID`.
- Calls `FatForceCacheMiss` for each relevant FCB/DCB.

This is used by directory rename handling to make stale child FCBs disappear before moving a subtree.

## Forcing Cache Misses

`FatForceCacheMiss` flushes and purges cache/section state for an FCB.

Preconditions and locking:

- Requires the VCB to be acquired exclusive or locked.
- Requires wait-capable context; otherwise raises `STATUS_CANT_WAIT`.
- For directory FCBs with children, acquires child FCB resources first to prevent parent directory pinning conflicts.
- Acquires the target FCB exclusive.
- Sets `FCB_STATE_FORCE_MISS_IN_PROGRESS` and clears `VCB_STATE_FLAG_DELETED_FCB` before work.

Flush/purge behavior:

- If `FlushType` is nonzero, calls `FatFlushFile`.
- If the flush did not delete the FCB, inspects section object pointers.
- Flushes image sections first with `MmFlushImageSection`, because data-section purge can make image sections go away but not vice versa.
- Purges data sections with `CcPurgeCacheSection`.

Cleanup:

- Releases any acquired child FCBs.
- If the FCB was not deleted during cache purge, clears `FCB_STATE_FORCE_MISS_IN_PROGRESS` and releases the FCB.
- If close deleted the FCB, close-side logic is expected to have released the resource before freeing.

## Key Dependencies

- Node type macros and FastFAT object model: VCB, FCB, DCB, CCB.
- Cache and memory manager: `CcPurgeCacheSection`, `MmFlushImageSection`.
- Flush helper: `FatFlushFile`.
- Tree walks: `FatGetNextFcbTopDown`.
- Delayed close: `FatFspClose`.

## Implementation Notes

The file is small but foundational. Correct `FsContext`/`FsContext2` setup is what lets the rest of FastFAT distinguish user files, directories, volume opens, internal directory streams, EA streams, and the virtual volume file. The purge path is carefully ordered around Cache Manager side effects: acting on an FCB can indirectly trigger final close and subtree teardown, so enumeration and resource release are structured around disappearing nodes.
