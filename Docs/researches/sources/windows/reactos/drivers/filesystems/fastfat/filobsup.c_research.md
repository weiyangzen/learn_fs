# File Research: sources/windows/reactos/drivers/filesystems/fastfat/filobsup.c

## Purpose

`filobsup.c` provides FastFAT file-object support routines. It attaches FastFAT VCB/FCB/DCB/CCB pointers to Windows file objects, decodes those pointers back into typed open kinds, and forces cache/section misses for FCB trees during operations such as volume lock, purge, rename, overwrite, or teardown.

The file is small but foundational: most dispatch paths rely on `FatDecodeFileObject` to classify handles, and several namespace/cache operations rely on `FatPurgeReferencedFileObjects` and `FatForceCacheMiss` to make cached sections disappear when possible.

## Main Functions

- `FatSetFileObject`
  - Initializes `FileObject->FsContext`, `FileObject->FsContext2`, and `FileObject->Vpb`.
  - Accepts the FastFAT open type and validates the expected object combination with assertions:
    - `UserFileOpen`: FCB plus CCB.
    - `EaFile`: FCB without CCB.
    - `UserDirectoryOpen`: DCB/root DCB plus CCB.
    - `UserVolumeOpen`: VCB plus CCB.
    - `VirtualVolumeFile`: VCB without CCB.
    - `DirectoryFile`: DCB/root DCB without CCB.
    - `UnopenedFileObject`: no backing object.
  - Copies the VCB’s VPB for volume opens or the owning FCB/DCB’s VCB VPB for file/directory opens.
  - Mirrors `FCB_STATE_TEMPORARY` into `FO_TEMPORARY_FILE`.

- `FatDecodeFileObject`
  - Reads `FsContext` and `FsContext2` and returns a `TYPE_OF_OPEN`.
  - If `FsContext` is null, returns `UnopenedFileObject`.
  - If `FsContext` is a VCB, returns `VirtualVolumeFile` or `UserVolumeOpen` depending on whether a CCB exists.
  - If `FsContext` is a DCB/root DCB, returns `DirectoryFile` or `UserDirectoryOpen`.
  - If `FsContext` is an FCB with a CCB, returns `UserFileOpen`.
  - If `FsContext` is an FCB without a CCB, returns `EaFile` only when the FCB is the volume EA FCB.
  - Bugchecks on unexpected node-type combinations because corrupted file-object context means the filesystem cannot safely continue.

- `FatPurgeReferencedFileObjects`
  - Forces delayed closes first with `FatFspClose`.
  - Walks the FCB/DCB subtree top-down using `FatGetNextFcbTopDown`.
  - Gets the next node before acting on the current node because purging can cause the current FCB and ancestors to vanish.
  - Skips volume-ID entries and calls `FatForceCacheMiss` on other nodes.
  - Requires a waitable IRP context.

- `FatForceCacheMiss`
  - Flushes and purges cache/MM sections for a single FCB/DCB.
  - Requires the VCB to be held exclusively or the volume to be locked.
  - Raises `STATUS_CANT_WAIT` if the IRP context is not waitable.
  - For directories with children, acquires child FCB resources first to avoid parent directory pinning and cache-manager deadlocks.
  - Acquires the target FCB exclusively, sets `FCB_STATE_FORCE_MISS_IN_PROGRESS`, and clears the VCB deleted-FCB marker.
  - Optionally flushes the file through `FatFlushFile`.
  - If the FCB was not deleted during the flush, flushes image sections before purging data cache sections.
  - Releases acquired child resources and releases the target FCB only if it survived the purge path.

## Key Dependencies and Integration

- All functions depend on FastFAT node type codes stored in common node headers.
- `FatSetFileObject` and `FatDecodeFileObject` are used throughout create, cleanup, close, query, set, flush, read/write, and FSCTL paths.
- `FatPurgeReferencedFileObjects` is used by higher-level operations that need cached sections closed before namespace or volume operations proceed.
- `FatForceCacheMiss` integrates with `FatFlushFile`, `MmFlushImageSection`, `CcPurgeCacheSection`, FCB resource acquisition, delayed-close processing, and VCB deleted-FCB state.

## Important Invariants

- File-object `FsContext` is the primary type discriminator for FastFAT opens.
- `FsContext2` being null or non-null distinguishes user opens from internal stream opens for the same node type.
- Cache purge can trigger final close and FCB deletion, so callers must not assume the FCB survives flush/purge.
- The next subtree node must be computed before purging the current node.
- `FatForceCacheMiss` must run only when waiting is allowed and namespace/volume synchronization prevents concurrent teardown races.

## Notable Risks

- A stale or corrupted `FsContext` causes a bugcheck rather than recoverable failure.
- Cache purge paths are sensitive to resource ordering between directories, children, cache-manager flush callbacks, and close teardown.
- Purging image sections before data sections is required because data purge can make image-section state disappear, but not the reverse.
- The implementation relies on VCB `VCB_STATE_FLAG_DELETED_FCB` to decide whether releasing the FCB is still legal after cache-manager activity.
