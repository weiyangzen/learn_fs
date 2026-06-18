# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatprocs.h

## Purpose

`fatprocs.h` is the central internal procedure header for the Windows Driver Samples FastFAT filesystem driver. It pulls in NT filesystem/storage headers plus FastFAT's core local headers, defines small inline helpers/macros, and declares the cross-module routines used by allocation, cache, device I/O, dirent, EA, file-object, filesystem-control, naming, resource, structure, splay-tree, time, verification, work-queue, FSD/FSP dispatch, completion, fast I/O, and FAT scanning code.

This file is primarily an integration map rather than an implementation unit. It establishes the public internal ABI between FastFAT modules and records many lock, wait, exception, and cache-manager contracts through SAL annotations and macros.

## Major Interfaces

- String and MCB helpers:
  - `FatFreeStringBuffer`, `FatExtendString`, and `FatEnsureStringBufferEnough` manage dynamically grown string buffers.
  - `FatAddMcbEntry`, `FatLookupMcbEntry`, `FatLookupLastMcbEntry`, `FatGetNextMcbEntry`, and `FatRemoveMcbEntry` wrap run-map maintenance.
- Access checks:
  - `FatCheckFileAccess`, `FatCheckManageVolumeAccess`, and `FatExplicitDeviceAccessGranted` gate file and volume operations against file attributes, access state, privilege, and target device access.
- Allocation support:
  - `FatLookupFatEntry`, `FatSetupAllocationSupport`, `FatTearDownAllocationSupport`, `FatLookupFileAllocation`, `FatAddFileAllocation`, `FatTruncateFileAllocation`, `FatLookupFileAllocationSize`, `FatAllocateDiskSpace`, `FatDeallocateDiskSpace`, `FatSplitAllocation`, `FatMergeAllocation`, `FatSetFatEntry`, `FatLogOf`, and `FatInterpretClusterType`.
  - `FAT_ENUMERATION_CONTEXT` tracks a pinned FAT page during cluster-chain enumeration.
  - `FatIsIoRangeValid()` is inline and enforces FAT's 32-bit file-size addressability: no high 32-bit start offset and no 32-bit wrap after adding length.
- Cache and buffer support:
  - Volume and directory cached access through `FatReadVolumeFile`, `FatPrepareWriteVolumeFile`, `FatReadDirectoryFile`, `FatPrepareWriteDirectoryFile`, and `FatOpenDirectoryFile`.
  - EA stream cache access through `FatOpenEaFile` and `FatCloseEaFile`.
  - BCB lifecycle helpers: `FatSetDirtyBcb`, `FatRepinBcb`, `FatUnpinRepinnedBcbs`, `FatPinMappedData`, and `FatUnpinBcb`.
  - Cache map setup and teardown through `FatInitializeCacheMap` and `FatSyncUninitializeCacheMap`.
  - `FatZeroData`, `FatCompleteMdl`, and `FatPrefetchPages` support zeroing, MDL completion, and read-ahead.
- Device I/O:
  - Paging, noncached, aligned/nonaligned, single-run, and multiple-run I/O paths via `FatPagingFileIo`, `FatNonCachedIo`, `FatNonCachedNonAlignedRead`, `FatMultipleAsync`, `FatSingleAsync`, and `FatWaitSync`.
  - User-buffer preparation through `FatLockUserBuffer`, `FatBufferUserBuffer`, and `FatMapUserBuffer`.
  - Storage control helpers through `FatToggleMediaEjectDisable`, `FatPerformDevIoCtrl`, and `FatBuildZeroMdl`.
- Dirent support:
  - Creation, initialization, deletion, search, label lookup, empty-directory checks, file deletion, dirent construction, file-size updates, and FCB-to-dirent synchronization through the `FatCreateNewDirent` through `FatUpdateDirentFromFcb` declarations.
  - `FatDirectoryKey` derives a static 64-bit key from creation time and first cluster.
- Extended attributes:
  - EA length/count/create/delete/file discovery/set add/delete/read helpers are declared for the OS/2-style `EA DATA. SF` backing file implementation.
  - Packed EA operations include delete, append, locate-next, locate-by-name, name validation, pin/dirty/unpin range operations.
  - `FatUpcaseEaName` maps to `RtlUpperString`.
  - `SizeOfFullEa` computes the unpadded size of a `FILE_FULL_EA_INFORMATION` entry.
- File object support:
  - `TYPE_OF_OPEN` classifies unopened, user file, user directory, user volume, virtual volume, directory stream, and EA stream opens.
  - `FAT_FLUSH_TYPE` selects no flush, flush, flush-and-invalidate, or flush-without-purge.
  - `FatSetFileObject`, `FatDecodeFileObject`, `FatPurgeReferencedFileObjects`, and `FatForceCacheMiss` maintain `FsContext` semantics and cache purge behavior.
- Filesystem control:
  - `FatFlushAndCleanVolume`, `FatIsBootSectorFat`, `FatLockVolumeInternal`, and `FatUnlockVolumeInternal`.
- Name support:
  - Fast equality and legality macros for OEM/Unicode short and long names.
  - `FatIsNameLongUnicodeValid()` inline-validates ASCII-range Unicode characters using HPFS legality rules and asserts that path and leading-backslash modes are not used.
  - Pattern matching, 8.3 conversion, Unicode name recovery, full-name construction, case evaluation, short-name selection, space detection, and case restoration are declared.
- Resources and cache callbacks:
  - Global, VCB, FCB, whole-volume, directory-file mutex, cache-manager lazy-write/read-ahead/flush, no-op, and create-section filter callbacks are declared or macro-defined.
  - `FatAcquireExclusiveVolume` and `FatReleaseVolume` acquire/release the VCB and all child FCB resources bottom-up/top-down around whole-volume operations.
  - `FatGetFcbOplock` adapts to the Win8 advanced FCB header oplock location.
- Structure support:
  - VCB, FCB, DCB, CCB, IRP context, dismount, close-context, and tree-walk lifecycle functions are declared.
  - Tree navigation macros `FatGetFirstChild` and `FatGetNextSibling` traverse DCB child queues.
  - `FatIsRawDevice` identifies media-not-ready/no-media statuses.
- Splay/name tree support:
  - `FatInsertName`, `FatRemoveNames`, `FatFindFcb`, `FatIsHandleCountZero`, `FatCompareNames`, and the `CompareNames` fast first-byte macro.
- Time and verification:
  - FAT/NT time conversion and current FAT timestamp routines.
  - `FAT_VOLUME_STATE`, FCB condition marking, VCB/FCB verification, clean-volume DPC, volume dirty/clean marking, dirty-bit checks, quick verify, operation legality, and `FatPerformVerify`.
- Work queue and dispatch:
  - Posting and worker dispatch helpers: `FatOplockComplete`, `FatPrePostIrp`, `FatAddToWorkque`, `FatFsdPostRequest`, and `FatFspDispatch`.
  - FSD driver dispatch declarations for cleanup, close, create, device control, directory control, query/set EA, query/set file info, flush, filesystem control, lock control, PnP, read, shutdown, query/set volume info, and write.
  - FSP/common routines for each major operation, including Windows Threshold stack-swapped create support.
- Flush/completion/fast I/O:
  - File, directory, FAT, volume, device flush, FAT-entry flush, and dirent flush routines.
  - `FatCompleteRequest_Real` and `FatCompleteRequest`.
  - Top-level IRP checks, file-corruption popup support, fast I/O possible/query/lock/unlock callbacks.
  - FAT media/entry scan helpers `FatExamineFatEntries` and `FatScanForDataTrack`.

## Important Macros and Contracts

- Pointer and alignment helpers: `Add2Ptr`, `PtrOffset`, `WordAlign`, `LongAlign`, `QuadAlign`, `BlockAlign`, and `BlockAlignTruncate`.
- Unaligned BPB copy helpers: `UCHAR1`, `UCHAR2`, `UCHAR4`, `CopyUchar1`, `CopyUchar2`, `CopyUchar4`, and `CopyU4char`.
- FAT type predicates: `FatIsFat32`, `FatIsFat16`, and `FatIsFat12`.
- VCB condition updates are traceable under `FASTFATDBG` through `FatSetVcbCondition`.
- Lock assertions and SAL annotations repeatedly require the global critical region and specify acquired VCB/FCB locks.
- `FatUnpinBcb` decrements `IrpContext->PinCount` only in checked builds, making pin leak diagnostics debug-only.
- `FatNotifyReportChange` lazily builds `FullFileName` and reports notify changes with the parent-name prefix length computed from `FinalNameLength`.
- `CanFsdWait(IRP)` expands to `IoIsOperationSynchronous(Irp)` and relies on the parameter name being `Irp` inside the macro expansion.
- `IsFileDeleted`, `IsFileWriteThrough`, `FatIsFastIoPossible`, `FatIsFileOplockable`, and `IsFileObjectReadOnly` encode common open-state decisions.
- Exception handling uses `FatExceptionFilter`, `FatProcessException`, `FatRaiseStatus`, `FatResetExceptionState`, `FatNormalizeAndRaiseStatus`, and debug-only `DebugBreakOnStatus`.
- `try_return` and `try_leave` implement the local try/finally return style by jumping to `try_exit`.
- File IDs are generated from parent dirent offsets and root/FAT32 location rules, with special handling for `.` and `..`.
- `FatDeviceIsFatFsdo` identifies the two filesystem device objects created by the driver.
- `IsDirectory` checks FCB node type for DCB/root DCB.

## Integration

`fatprocs.h` binds together structures from `FatStruc.h`, globals from `FatData.h`, on-disk FAT structures from `Fat.h`, LFN definitions from `Lfn.h`, node type codes from `nodetype.h`, and Windows kernel interfaces from `ntifs.h` plus storage/CDROM/SCSI/DDI headers. Most FastFAT implementation files include it, so changes here affect the whole driver.

The header also exposes cross-version conditionals:
- Win8 and later use `FSRTL_ADVANCED_FCB_HEADER` oplock storage for files and directories.
- Pre-Win8 keeps the oplock in the file-specific union member.
- Windows Threshold and later enable stack-swapped create callout declarations.

## Notable Risks and Review Points

- Many macros evaluate parameters more than once and are not expression-safe in all contexts.
- Alignment helpers cast through `ULONG`, so they are intended for FAT 32-bit offsets and not arbitrary 64-bit pointer arithmetic.
- `FatAcquireExclusiveVolume` and `FatReleaseVolume` walk all child FCBs while locking; caller lock ordering must remain consistent to avoid deadlocks.
- `FatNotifyReportChange` assumes `FullFileName` and `FinalNameLength` invariants and asserts rather than gracefully handling malformed FCB names.
- Exception state is stored in `IrpContext`; handlers that catch and continue must reset it or a later unrelated exception can be misclassified.
- The declarations distinguish waitable and non-waitable operation through `FINISHED`, but correctness depends on every implementation honoring `IRP_CONTEXT_FLAG_WAIT`.
- `FatIsIoRangeValid()` ignores `Vcb` and only enforces 32-bit wrap constraints. Cluster-size or volume-bound checks must be done elsewhere.
