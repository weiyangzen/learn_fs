# File Research: sources/windows/reactos/drivers/filesystems/udfs/create.cpp

## Purpose

`create.cpp` implements the ReactOS UDFS `IRP_MJ_CREATE` path. It handles all open/create forms for UDF volumes, root directories, regular files, directories, named streams, duplicate/reopen requests, and file-id opens. It also initializes FCB/CCB state for first opens and binds successful creates to NT `FILE_OBJECT` structures.

## Main Entry Points

- `UDFCreate(PDEVICE_OBJECT, PIRP)`: top-level create dispatch routine registered from `udfinit.cpp`. It enters the filesystem, handles direct opens of the filesystem control device object, creates an IRP context, calls `UDFCommonCreate`, and routes exceptions through the driver exception/logging path.
- `UDFCommonCreate(PtrUDFIrpContext, PIRP)`: central create/open implementation. It decodes create options/disposition, validates volume state, resolves paths, opens or creates the requested object, checks access/share rules, handles overwrite/supersede, completes the IRP, and unwinds intermediate open state on failure.
- `UDFReleaseResFromCreate(PERESOURCE*, PERESOURCE*, PERESOURCE*)`: cleanup helper that releases the paging I/O resource plus two ordinary resources if held.
- `UDFAcquireParent(PUDF_FILE_INFO, PERESOURCE*, PERESOURCE*)`: acquires parent/current FCB main resources and bumps references while path traversal is using a parent chain.
- `UDFFirstOpenFile(...)`: allocates and initializes an FCB and NT-required FCB state for a file info object that has not yet been opened through the FSD.
- `UDFOpenFile(PVCB, PFILE_OBJECT, PtrUDFFCB)`: allocates a CCB, attaches it to a `FILE_OBJECT`, links the CCB into the FCB, and increments reference counts.
- `UDFInitializeFCB(...)`: initializes FCB bookkeeping, resources, file lock, list links, name, flags, and VCB association.

## Create/Open Flow

`UDFCreate` first rejects no-op FSD-device opens by completing them as `FILE_OPENED`. For volume-device opens, it establishes top-level IRP state and delegates to `UDFCommonCreate`.

`UDFCommonCreate` performs the real work:

1. It decodes `FILE_OBJECT`, related file object, desired access, share access, allocation size, file attributes, create disposition, and create option flags.
2. It rejects unsupported early cases such as paging-file creation and nonzero EA length.
3. It obtains the VCB, flush-breaks pending work, denies creates during soft eject, denies foreign-PID access to locked volumes, verifies the VCB, and downgrades the VCB resource from exclusive to shared after verification.
4. It enforces read-only or dirty-open volume restrictions before any modifying operation.
5. It special-cases volume opens, root-directory opens, open-by-file-id, relative opens, duplicate-handle/reopen requests, stream paths, open-target-directory requests, missing-object creates, and existing-object opens.
6. It completes success by setting `FILE_OBJECT` flags, CCB flags, open counts, readonly counts, valid FCB flags, `IoStatus.Information`, and final IRP status.
7. It completes failure by removing share access when needed, cleaning CCB state, closing intermediate `UDF_FILE_INFO` chains, cleaning FCB chains, releasing resources, and freeing path buffers.

## Path Resolution

The routine constructs an absolute path from either the target name or a related directory object. Relative opens require the related object to be a directory and reject absolute target names. It normalizes leading double backslashes, trims trailing backslashes, validates total path and component lengths, and calls `UDFIsNameValid` to detect invalid characters and stream syntax.

Traversal uses `UDFDissectName` to split path components. Each component is opened through `UDFOpenFile__` for normal files/directories or `UDFOpenStreamDir__`/`UDFCreateStreamDir__` for stream directories. The loop keeps `LastGoodFileInfo`, `LastGoodName`, `LastGoodTail`, `OldRelatedFileInfo`, and `TreeLength` so it can distinguish a valid parent from a missing final component and unwind internal opens accurately.

`FILE_OPEN_BY_FILE_ID` is translated into an absolute path by `UDFGetOpenParamsByFileId`, after which the normal absolute open path is reused.

## Volume and Root Opens

Volume opens are identified by an empty file name with no non-volume related object. The code rejects invalid directory-only/delete/create semantics for volumes, checks whether the desired access/share combination implies read-only or read-write volume access, optionally flushes and closes delayed handles before exclusive-like opens, and may set `UDF_VCB_FLAGS_VOLUME_LOCKED`. It opens the VCB as the FCB, marks the CCB as `UDF_CCB_VOLUME_OPEN`, checks security/share access, forces no intermediate buffering, reports `FILE_OPENED`, and emits a volume event hook.

Root opens are identified by an absolute path length of one backslash. The code rejects file-only, supersede, overwrite, and delete-on-close requests; opens `Vcb->RootDirFCB`; references the root file info; checks access/share; and returns `FILE_OPENED`.

## Create, Stream, Overwrite, and Supersede Behavior

If traversal fails on the final object with `STATUS_OBJECT_NAME_NOT_FOUND` or `STATUS_OBJECT_PATH_NOT_FOUND`, `UDFCommonCreate` creates only for `FILE_CREATE`, `FILE_OPEN_IF`, `FILE_OVERWRITE_IF`, or `FILE_SUPERSEDE`. It checks volume writability, delete-on-close with readonly attributes, parent add-file/add-subdirectory access, target-name validity, and directory-versus-stream restrictions.

New objects are created with `UDFCreateFile__`, optionally converted into directories with `UDFRecordDirectory__`, assigned NT archive attributes for files, opened through `UDFFirstOpenFile`, initialized to zero length, and passed through `UDFSetAccessRights`. Notify events report file, directory, or stream additions.

Named stream creation can involve three phases: open/create the base file, create/open the stream directory, then create/open the stream entry. The code marks the underlying FCB valid between phases and updates `LocalPath` and `TreeLength` for unwind.

Existing objects go through `AlreadyOpened`. `FILE_CREATE` returns `STATUS_OBJECT_NAME_COLLISION`. Directory-only/file-only mismatches are rejected. Delete-on-close rejects readonly files and non-empty directories. Existing-object overwrite/supersede checks delete or write permissions, verifies system/hidden attribute compatibility, rejects mapped-file truncation via `MmCanFileBeTruncated`, synchronizes with `PagingIoResource`, truncates using `UDFResizeFile__`, updates allocation/file/valid lengths, calls `CcSetFileSizes`, adjusts attributes, and emits modify notifications.

## FCB/CCB Initialization

`UDFFirstOpenFile` allocates a UDF FCB and object name, links the FCB to `UDF_FILE_INFO`, attaches or allocates the shared `UDFNTRequiredFCB` stored in the file's `Dloc->CommonFcb`, seeds sizes/timestamps from on-disk metadata for new common FCBs, inserts the FCB under `Vcb->FcbListResource`, initializes readonly/directory flags, appends the final on-disk name, and optionally calls `UDFOpenFile`.

`UDFInitializeFCB` initializes `FSRTL_COMMON_FCB_HEADER` resource pointers, main and paging resources, file locks, common reference count, CCB list resource, VCB FCB list link, CCB list head, counters, flags, name pointer, and owning VCB.

`UDFOpenFile` allocates a CCB, stores the FCB and file object, fills `FsContext`, `FsContext2`, `Vpb`, and `SectionObjectPointer`, clears delayed-close state, links the CCB into `NextCCB`, and increments FCB/common reference counts.

## Synchronization and State

The create path uses `Vcb->VCBResource`, FCB `MainResource`, and, for truncation, `PagingIoResource`. It carefully tracks `Res1`, `Res2`, and `PagingIoRes` to avoid leaking locks across early exits. It temporarily increments `VCBOpenCount` around flush/close-all operations that release the VCB resource.

Successful opens update `VCBHandleCount`, per-FCB `OpenHandleCount`, `CachedOpenHandleCount`, `VCBOpenCount`, and optionally `VCBOpenCountRO`. CCB flags record delete-on-close, case-sensitive opens, readonly opens, volume opens, and tree length. File-object flags are set for write-through, sequential I/O, no buffering, cache support, execute fast I/O, case sensitivity, and stream opens.

## Integration Points

This file depends heavily on:

- `udf_info` primitives: `UDFOpenFile__`, `UDFCreateFile__`, `UDFCloseFile__`, `UDFCreateStreamDir__`, `UDFOpenStreamDir__`, `UDFRecordDirectory__`, `UDFResizeFile__`, `UDFUnlinkFile__`.
- Access/security helpers: `UDFCheckAccessRights`, `UDFSetAccessRights`, `UdfIllegalFcbAccess`.
- VCB and volume helpers: `UDFVerifyVcb`, `UDFFlushTryBreak`, `UDFFlushLogicalVolume`, delayed-close cleanup helpers, lock/eject state.
- Cache/memory manager APIs: `CcIsFileCached`, `CcSetFileSizes`, `CcFlushCache`, `CcPurgeCacheSection`, `MmFlushImageSection`, `MmCanFileBeTruncated`.
- Notification helpers from `env_spec.h`: `UDFNotifyFullReportChange`, `UDFNotifyVolumeEvent`.

## Notable Risks and Edge Cases

- The routine is long and stateful; many early exits depend on correct `TreeLength`, `LastGoodFileInfo`, and resource pointer maintenance.
- Stream creation has multi-phase partial state and complex cleanup paths; failed stream directory or stream entry creation can leave metadata to flush/unlink.
- Duplicate-handle/reopen handling simulates normal traversal by backing up to the parent, which depends on parent references and FCB links being valid.
- Some fields and comments preserve historical NT behavior, including allowing create of readonly files with write access before later denial.
- Several paths are conditionally compiled around `UDF_READ_ONLY_BUILD` and `IFS_40`, so write behavior can differ materially by build.
- Volume locking and flush behavior relies on open/share counts and delayed close cleanup; incorrect counts can affect dismount/lock correctness.

## Testing Signals

Useful tests would cover volume/root opens, relative opens, duplicate-handle opens, file-id opens, case-sensitive opens, create/open/open-if dispositions, delete-on-close, readonly media and readonly-file denial, stream creation/open, target-directory opens for rename, noncached opens with existing cache sections, mapped-file overwrite denial, and unwind after injected failures in `UDFCreateFile__`, `UDFFirstOpenFile`, and `UDFSetAccessRights`.
