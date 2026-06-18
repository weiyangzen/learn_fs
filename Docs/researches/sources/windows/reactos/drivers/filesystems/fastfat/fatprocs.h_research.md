# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatprocs.h

## Purpose

`fatprocs.h` is the central internal procedure header for the FastFAT filesystem. It includes NT kernel headers, FAT structure headers, ReactOS compatibility shims, shared helper macros, and prototypes for the driver’s major subsystems.

It is the main internal ABI between FastFAT modules.

## Included Dependencies

- NT filesystem/device headers: `ntifs.h`, `ntddscsi.h`, `scsi.h`, `ntddcdrm.h`, `ntdddisk.h`, `ntddstor.h`, `ntintsafe.h`.
- ReactOS-specific headers under `__REACTOS__`: `pseh/pseh2.h`, `dbgbitmap.h`.
- Local headers:
  - `nodetype.h`
  - `fat.h`
  - `lfn.h`
  - `fatstruc.h`
  - `fatdata.h`

## ReactOS Compatibility Adjustments

Under `__REACTOS__`, this header downgrades unsupported NT 6.2+ memory/security features:

- `MdlMappingNoExecute` becomes `0`.
- `NonPagedPoolNx` maps to `NonPagedPool`.
- `NonPagedPoolNxCacheAligned` maps to `NonPagedPoolCacheAligned`.
- `POOL_NX_ALLOCATION` becomes `0`.

It also defines `TYPE_OF_OPEN` before `fatstruc.h`, because `fatstruc.h` needs it.

## Major Type and Macro Definitions

- `FINISHED`: Boolean result convention for operations that may fail only because waiting/blocking was not allowed.
- `FAT_CREATE_INITIAL_NAME_BUF_SIZE`: stack buffer size for create/rename name components.
- `FAT_ENUMERATION_CONTEXT`: tracks a pinned FAT page during FAT entry enumeration.
- `TYPE_OF_OPEN`: identifies file object interpretation:
  - `UnopenedFileObject`
  - `UserFileOpen`
  - `UserDirectoryOpen`
  - `UserVolumeOpen`
  - `VirtualVolumeFile`
  - `DirectoryFile`
  - `EaFile`
- `FAT_FLUSH_TYPE`: flush/purge modes.
- `COMPARISON`: name comparison result.
- `FAT_VOLUME_STATE`: clean/dirty volume marking modes.
- Alignment and pointer helpers: `Add2Ptr`, `PtrOffset`, `WordAlign`, `LongAlign`, `QuadAlign`, `BlockAlign`, `BlockAlignTruncate`.
- Unaligned field copy helpers: `CopyUchar1`, `CopyUchar2`, `CopyUchar4`, `CopyU4char`.

## Functional Areas Declared

### String and MCB Helpers

Declares string buffer management and MCB mapping helpers:

- `FatFreeStringBuffer`
- `FatExtendString`
- `FatEnsureStringBufferEnough`
- `FatAddMcbEntry`
- `FatLookupMcbEntry`
- `FatLookupLastMcbEntry`
- `FatGetNextMcbEntry`
- `FatRemoveMcbEntry`

### Access Checks

Declares access validation helpers:

- `FatCheckFileAccess`
- `FatCheckManageVolumeAccess`
- `FatExplicitDeviceAccessGranted`

### Allocation Support

Declares FAT cluster/allocation operations:

- `FatLookupFatEntry`
- `FatSetupAllocationSupport`
- `FatTearDownAllocationSupport`
- `FatLookupFileAllocation`
- `FatAddFileAllocation`
- `FatTruncateFileAllocation`
- `FatLookupFileAllocationSize`
- `FatAllocateDiskSpace`
- `FatDeallocateDiskSpace`
- `FatSplitAllocation`
- `FatMergeAllocation`
- `FatSetFatEntry`
- `FatLogOf`

The inline `FatIsIoRangeValid` enforces FAT’s 32-bit file-size addressability limit.

### Cache and Buffer Support

Declares volume/directory cache access, cache-map setup, BCB pinning/dirtying, MDL completion, prefetching, and zeroing:

- `FatReadVolumeFile`
- `FatPrepareWriteVolumeFile`
- `FatReadDirectoryFile`
- `FatPrepareWriteDirectoryFile`
- `FatOpenDirectoryFile`
- `FatSetDirtyBcb`
- `FatRepinBcb`
- `FatUnpinRepinnedBcbs`
- `FatZeroData`
- `FatInitializeCacheMap`
- `FatSyncUninitializeCacheMap`

`FatUnpinBcb` is a macro; debug builds decrement `IrpContext->PinCount`.

### Device I/O

Declares noncached and paging I/O helpers:

- `FatPagingFileIo`
- `FatNonCachedIo`
- `FatNonCachedNonAlignedRead`
- `FatMultipleAsync`
- `FatSingleAsync`
- `FatWaitSync`
- `FatLockUserBuffer`
- `FatBufferUserBuffer`
- `FatMapUserBuffer`
- `FatToggleMediaEjectDisable`
- `FatPerformDevIoCtrl`
- `FatBuildZeroMdl`

### Directory Entry Support

Declares dirent creation, lookup, deletion, construction, and synchronization with FCB state:

- `FatCreateNewDirent`
- `FatInitializeDirectoryDirent`
- `FatDeleteDirent`
- `FatLocateDirent`
- `FatLocateSimpleOemDirent`
- `FatLfnDirentExists`
- `FatLocateVolumeLabel`
- `FatGetDirentFromFcbOrDcb`
- `FatIsDirectoryEmpty`
- `FatDeleteFile`
- `FatConstructDirent`
- `FatConstructLabelDirent`
- `FatSetFileSizeInDirent`
- `FatUpdateDirentFromFcb`

`FatDirectoryKey` derives a 64-bit directory key from creation time and first cluster.

### Extended Attributes

Declares EA file and packed-EA manipulation:

- `FatGetEaLength`
- `FatGetNeedEaCount`
- `FatCreateEa`
- `FatDeleteEa`
- `FatGetEaFile`
- `FatReadEaSet`
- `FatDeleteEaSet`
- `FatAddEaSet`
- `FatDeletePackedEa`
- `FatAppendPackedEa`
- `FatLocateNextEa`
- `FatLocateEaByName`
- `FatIsEaNameValid`
- `FatPinEaRange`
- `FatMarkEaRangeDirty`
- `FatUnpinEaRange`

### File Object Support

Declares mapping between NT file objects and FastFAT objects:

- `FatSetFileObject`
- `FatDecodeFileObject`
- `FatPurgeReferencedFileObjects`
- `FatForceCacheMiss`

### Filesystem Control

Declares volume flush, boot-sector validation, and lock/unlock helpers:

- `FatFlushAndCleanVolume`
- `FatIsBootSectorFat`
- `FatLockVolumeInternal`
- `FatUnlockVolumeInternal`

### Name Support

Declares short/long name validation, 8.3 conversion, Unicode/OEM conversion, LFN selection, and case restoration:

- `FatIsNameInExpression`
- `FatStringTo8dot3`
- `Fat8dot3ToString`
- `FatGetUnicodeNameFromFcb`
- `FatSetFullFileNameInFcb`
- `FatSetFullNameInFcb`
- `FatUnicodeToUpcaseOem`
- `FatSelectNames`
- `FatEvaluateNameCase`
- `FatSpaceInName`
- `FatUnicodeRestoreShortNameCase`

Inline/macro helpers include:

- `FatAreNamesEqual`
- `FatIsNameShortOemValid`
- `FatIsNameLongOemValid`
- `FatIsNameLongUnicodeValid`

### Resource and Locking Model

Defines the core locking protocol:

- Global resource: `FatData.Resource`
- Volume resource: `Vcb->Resource`
- File resource: `Fcb->Header.Resource`

Macros and routines include:

- `FatAcquireExclusiveGlobal`
- `FatAcquireSharedGlobal`
- `FatAcquireExclusiveVolume`
- `FatReleaseVolume`
- `FatAcquireExclusiveVcb`
- `FatAcquireSharedVcb`
- `FatAcquireExclusiveFcb`
- `FatAcquireSharedFcb`
- `FatAcquireSharedFcbWaitForEx`
- `FatConvertToSharedFcb`
- `FatReleaseGlobal`
- `FatReleaseVcb`
- `FatReleaseFcb`

The comments document a clear acquisition hierarchy: global first, then VCB or FCB, with mount/dismount taking the global resource exclusive.

### Cache Manager and Filter Callbacks

Declares cache callback routines:

- `FatAcquireVolumeForClose`
- `FatReleaseVolumeFromClose`
- `FatAcquireFcbForLazyWrite`
- `FatReleaseFcbFromLazyWrite`
- `FatAcquireFcbForReadAhead`
- `FatReleaseFcbFromReadAhead`
- `FatAcquireForCcFlush`
- `FatReleaseForCcFlush`
- `FatNoOpAcquire`
- `FatNoOpRelease`
- `FatFilterCallbackAcquireForCreateSection`

### Structure Lifecycle

Declares constructors/destructors and traversal helpers:

- `FatInitializeVcb`
- `FatTearDownVcb`
- `FatDeleteVcb`
- `FatCreateRootDcb`
- `FatCreateFcb`
- `FatCreateDcb`
- `FatDeleteFcb`
- `FatCreateCcb`
- `FatDeleteCcb`
- `FatCreateIrpContext`
- `FatDeleteIrpContext_Real`
- `FatGetNextFcbTopDown`
- `FatGetNextFcbBottomUp`
- `FatCheckForDismount`

### Splay Tree Name Indexes

Declares open-FCB name index operations:

- `FatInsertName`
- `FatRemoveNames`
- `FatFindFcb`
- `FatIsHandleCountZero`
- `FatCompareNames`

`CompareNames` optimizes comparison by first byte before full compare.

### Time Conversion

Declares FAT/NT timestamp conversions:

- `FatNtTimeToFatTime`
- `FatFatTimeToNtTime`
- `FatFatDateToNtTime`
- `FatGetCurrentFatTime`

### Verification and Dirty State

Declares media/volume verification and dirty marking:

- `FatMarkFcbCondition`
- `FatVerifyVcb`
- `FatVerifyFcb`
- `FatCleanVolumeDpc`
- `FatMarkVolume`
- `FatFspMarkVolumeDirtyWithRecover`
- `FatCheckDirtyBit`
- `FatQuickVerifyVcb`
- `FatVerifyOperationIsLegal`
- `FatPerformVerify`

### Work Queue

Declares posting and worker dispatch support:

- `FatOplockComplete`
- `FatPrePostIrp`
- `FatAddToWorkque`
- `FatFsdPostRequest`
- `FatFspDispatch`

### Dispatch Surface

Declares all FSD dispatch routines registered in `fatinit.c`:

- `FatFsdCleanup`
- `FatFsdClose`
- `FatFsdCreate`
- `FatFsdDeviceControl`
- `FatFsdDirectoryControl`
- `FatFsdQueryEa`
- `FatFsdSetEa`
- `FatFsdQueryInformation`
- `FatFsdSetInformation`
- `FatFsdFlushBuffers`
- `FatFsdFileSystemControl`
- `FatFsdLockControl`
- `FatFsdPnp`
- `FatFsdRead`
- `FatFsdShutdown`
- `FatFsdQueryVolumeInformation`
- `FatFsdSetVolumeInformation`
- `FatFsdWrite`

Also declares corresponding `FatCommon*` routines used by FSD/FSP paths.

### Fast I/O

Declares fast I/O callbacks:

- `FatFastIoCheckIfPossible`
- `FatFastQueryBasicInfo`
- `FatFastQueryStdInfo`
- `FatFastQueryNetworkOpenInfo`
- `FatFastLock`
- `FatFastUnlockSingle`
- `FatFastUnlockAll`
- `FatFastUnlockAllByKey`

`FatIsFastIoPossible` derives Fast I/O eligibility from FCB condition, node type, oplock state, byte-range locks, async writes, and write protection.

### Exception Handling

Declares and defines the driver’s structured exception convention:

- `FatExceptionFilter`
- `FatBugCheckExceptionFilter`
- `FatProcessException`
- `FatRaiseStatus`
- `FatResetExceptionState`
- `FatNormalizeAndRaiseStatus`
- `try_return`
- `try_leave`

`FatRaiseStatus` records expected errors in `IrpContext->ExceptionStatus` before raising.

### FAT-Specific Helpers

- `FatInterpretClusterType`
- `FatGenerateFileIdFromDirentOffset`
- `FatGenerateFileIdFromFcb`
- `FatGenerateFileIdFromDirentAndOffset`
- `FatDeviceIsFatFsdo`
- `IsDirectory`
- `IsFileDeleted`
- `IsFileWriteThrough`
- `IsFileObjectReadOnly`

## Research Notes

This header is the coordination point for the entire FastFAT implementation. It exposes module boundaries through comment headings, so it doubles as an architecture map: allocation, cache, device I/O, directory, EA, file-object, filesystem-control, name, resource, structure, splay, time, verification, work queue, FSD/FSP dispatch, Fast I/O, and exception-handling concerns are all declared here.

The most important design point is the explicit resource hierarchy and the distinction between FSD synchronous dispatch, FSP worker-thread processing, and Fast I/O shortcuts.
