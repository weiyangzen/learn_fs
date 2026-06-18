# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_info.h

## Purpose

`udf_info.h` is the private support API header for the UDFS metadata layer. It declares the functions implemented in `udf_info.cpp` and neighboring UDF modules, plus inline wrappers and macros for common file, extent, directory-index, bitmap, allocation, stream, and verification-cache operations.

The header includes `ecma_167.h`, `osta_misc.h`, `udf_rel.h`, and `wcache.h`, so it bridges UDF on-disk descriptor definitions, OSTA Unicode helpers, driver-local state definitions, and write-cache/verification support.

## API Surface

### Extent and Mapping Operations

The header declares operations for translating and using UDF extents:

- `UDFExtentOffsetToLba`, `UDFLocateLbaInExtent`, `UDFGetExtentLength`, `UDFGetMappingLength`.
- `UDFReadExtent`, `UDFWriteExtent`, `UDFZeroExtent`, and `UDFReadExtentLocation`.
- `UDFMergeMappings`, `UDFExtentToMapping`, `UDFPackMapping`, and `UDFUnPackMapping`.
- Allocation descriptor parsers: `UDFShortAllocDescToMapping`, `UDFLongAllocDescToMapping`, `UDFExtAllocDescToMapping`, `UDFReadMappingFromXEntry`.
- Conversion and mutation helpers for allocation state: `UDFMarkAllocatedAsRecorded`, `UDFMarkNotAllocatedAsAllocated`, `UDFMarkAllocatedAsNotXXX`, and wrappers for sparse/unrecorded allocation transitions.

These APIs establish that UDFS represents file storage as `EXTENT_INFO` containing a mapping array, logical length, offset, flags, and modification state.

### Directory Index and File Lookup

Directory operations include:

- `UDFDirIndexGetFrame`, `UDFDirIndexFree`, `UDFDirIndexGrow`, `UDFDirIndexTrunc`.
- `UDFDirIndexInitScan`, `UDFDirIndexScan`, `UDFIndexDirectory`.
- `UDFFindFile` and inline `UDFFindFile__`.
- `UDFGetDirIndexByFileInfo`, `UDFIsDirEmpty`, `UDFDirIndexGetLastIndex`.
- `UDFDirIndex` inline access, with x86 optimized declaration and generic frame-based lookup.

The directory index is frame-based unless `UDF_LIMIT_DIR_SIZE` is enabled. `UDF_DIR_INDEX_FRAME_SH` is 9 normally and 7 in limited/demo builds. `AlignDirIndex` aligns directory index counts to 32-entry granularity.

### File Entry, File Ident, and File Lifecycle APIs

The header declares the main file-object routines:

- FE/FileIdent construction and loading: `UDFReadFileEntry`, `UDFBuildFileEntry`, `UDFBuildFileIdent`, `UDFLoadExtInfo`, `UDFSetUpTag`.
- File lifecycle: `UDFOpenFile__`, `UDFOpenRootFile__`, `UDFCreateFile__`, `UDFCreateRootFile__`, `UDFCloseFile__`, `UDFCleanUpFile__`, `UDFUnlinkFile__`, `UDFUnlinkAllFilesInDir`.
- Data operations: inline `UDFReadFile__`, inline `UDFReadFileLocation__`, `UDFWriteFile__`, `UDFZeroFile__`, `UDFSparseFile__`, `UDFResizeFile__`, `UDFPadLastSector`.
- Metadata flush: `UDFFlushFE`, `UDFFlushFI`, `UDFFlushFile__`, and `UDFIsFlushed`.
- Rename/link/directory conversion: `UDFRenameMoveFile__`, `UDFHardLinkFile__`, `UDFRecordDirectory__`, `UDFPackDirectory__`, `UDFReTagDirectory`, `UDFPretendFileDeleted__`.
- Stream support: `UDFCreateStreamDir__`, `UDFOpenStreamDir__`, and stream-state macros.

The header also defines cleanup return flags: `UDF_FREE_NOTHING`, `UDF_FREE_FILEINFO`, and `UDF_FREE_DLOC`.

### Allocation, Free Space, and Partition Helpers

Allocation and free-space APIs include:

- `UDFGetBitmapLen`, `UDFFindMinSuitableExtent`, `UDFAllocFreeExtent`.
- `UDFMarkSpaceAsXXXNoProtect`, `UDFMarkSpaceAsXXX`, and optional `UDFCheckSpaceAllocation`.
- Allocation-state constants `AS_FREE`, `AS_USED`, `AS_DISCARDED`, and `AS_BAD`.
- FE allocation helpers: `UDFAllocateFESpace`, `UDFFreeFESpace`, `UDFFlushFESpace`, `UDFFreeFileAllocation`.
- Cached allocation helpers: `UDFGetCachedAllocation`, `UDFStoreCachedAllocation`, `UDFFlushAllCachedAllocations`.
- Partition translation and bounds: `UDFPhysLbaToPart`, `UDFPartLbaToPhys`, `UDFGetPartNumByPhysLba`, `UDFPartStart`, `UDFPartEnd`, `UDFPartLen`, `UDFGetPartNumByPartNdx`.
- Free/zero bitmap descriptor support: `UDFAddXSpaceBitmap`, `UDFDelXSpaceBitmap`, `UDFBuildFreeSpaceBitmap`, `UDFPrepareXSpaceBitmap`, `UDFUpdateXSpaceBitmaps`.

Several macros add optional tracking parameters when `UDF_TRACK_ONDISK_ALLOCATION` or `UDF_TRACK_ALLOC_FREE_EXTENT` is enabled, using `UDF_BUG_CHECK_ID` and `__LINE__`.

### Volume, Mount, VAT, and Descriptor Sequence APIs

The header exposes volume-recognition and mount-time functions:

- `UDFFindAnchor`, `UDFFindVRS`, `UDFReadTagged`.
- `UDFLoadPVolDesc`, `UDFLoadLogicalVolInt`, `UDFLoadLogicalVol`, `UDFLoadPartDesc`.
- `UDFReadVDS`, `UDFProcessSequence`, `UDFVerifySequence`, `UDFLoadFileset`, `UDFLoadPartition`, `UDFGetDiskInfoAndVerify`.
- Update/unmount helpers: `UDFUpdatePartDesc`, `UDFUpdateLogicalVolInt`, `UDFUpdateUSpaceDesc`, `UDFUpdateVDS`, `UDFUmount__`, `UDFUpdateVolIdent`.
- VAT support: `UDFLoadVAT`, `UDFRecordVAT`, `UDFModifyVAT`, `UDFUpdateVAT`.

The `UDFGetLVIDiUse` macro computes the implementation-use structure address inside a Logical Volume Integrity Descriptor after the per-partition free/size arrays.

### Dloc and Linked FileInfo Management

The header declares the shared data-location table API:

- `UDFFindDloc`, `UDFFindFreeDloc`, `UDFAcquireDloc`, `UDFReleaseDloc`.
- `UDFStoreDloc`, `UDFRemoveDloc`, `UDFUnlinkDloc`, `UDFFreeDloc`, `UDFRelocateDloc`, `UDFReleaseDlocList`.
- `UDFLocateParallelFI`, `UDFLocateAnyParallelFI`, and `UDFInsertLinkedFile`.

These functions support hard links, stream directories, parallel opens, and shared FE/data mapping state.

### Name, Attribute, Link, UID, and Counter Helpers

The header declares:

- `UDFDecompressUnicode`, `UDFCompressUnicode`, `UDFBuildHashEntry`.
- DOS name translation variants: `UDFDOSName`, `UDFDOSName201`, `UDFDOSName200`, `UDFDOSName100`, and `UDFDOSName__`.
- `UDFUnicodeInString`, `UDFIsIllegalChar`, `UDFUnicodeCksum`, `UDFUnicodeCksum150`, `UDFCrc`, `crc32`.
- File size and allocation descriptor length accessors: `UDFSetFileSize`, `UDFSetFileSizeInDirNdx`, `UDFGetFileSize`, `UDFGetFileSizeFromDirNdx`, `UDFSetAllocDescLen`.
- Link-count helpers: `UDFChangeFileLinkCount`, `UDFIncFileLinkCount`, `UDFDecFileLinkCount`, `UDFGetFileLinkCount`, optional `UDFSetFileLinkCount`.
- EntityID and UID helpers: `UDFSetEntityID_imp_`, `UDFSetEntityID_imp`, `UDFReadEntityID_Domain`, `UDFSetFileUID`, `UDFGetFileUID`.
- Volume counters: `UDFChangeFileCounter`, `UDFIncFileCounter`, `UDFDecFileCounter`, `UDFIncDirCounter`, `UDFDecDirCounter`.

### FileInfo and Stream Macros

Important inline/macro policies:

- `UDFIsDeleted` checks `FILE_DELETED`.
- `UDFIsADirectory` treats either a loaded directory index or a FileIdent `FILE_DIRECTORY` bit as directory evidence.
- `UDFGetFileAllocationSize` returns mapped data allocation length or one logical block.
- `UDFReferenceFile__`, `UDFReferenceFileEx__`, and `UDFDereferenceFile__` update `FileInfo->RefCount`, `Dloc->LinkRefCount`, and parent open counts.
- `UDFSetFileAllocMode__`, `UDFGetFileAllocMode__`, and `UDFGetFileICBAllocMode__` manipulate allocation-mode bits.
- `UDFStreamsSupported` and `UDFNtAclSupported` require `maxUDFWriteRev >= 0x0200`.
- `UDFIsAStreamDir`, `UDFHasAStreamDir`, `UDFIsAStream`, and `UDFIsSDirDeleted` test stream-directory FE flags.

### Bitmap Bit Operations

The header defines bit operations for free-space, bad-space, and zero-space bitmaps:

- On x86, external optimized routines are declared for `UDFGetBit__`, `UDFSetBit__`, `UDFSetBits__`, `UDFClrBit__`, and `UDFClrBits__`.
- On generic builds, macros directly manipulate 32-bit bitmap words.
- Semantic aliases invert or reuse raw bits for used/free state: `UDFGetUsedBit` is `!UDFGetBit`, while `UDFGetFreeBit` is `UDFGetBit`.

Optional allocation-owner tracking macros are enabled only under debug/console plus `UDF_TRACK_ONDISK_ALLOCATION_OWNERS`.

### Verification Cache API

The bottom of the header declares a verification/cache layer:

- Constants: `UDF_MAX_VERIFY_CACHE`, `UDF_VERIFY_CACHE_LOW`, `UDF_VERIFY_CACHE_GRAN`, `UDF_SYS_CACHE_STOP_THR`.
- I/O flags: `PH_FORGET_VERIFIED`, `PH_READ_VERIFY_CACHE`, `PH_KEEP_VERIFY_CACHE`.
- Lifecycle and I/O: `UDFVInit`, `UDFVRelease`, `UDFVWrite`, `UDFVRead`, `UDFVForget`, `UDFVVerify`, `UDFVFlush`.
- `UDFVIsStored` inline checks whether a logical block is present in `Vcb->VerifyCtx.StoredBitMap`.
- `UDFCheckArea` verifies an LBA range.

## Compile-Time Shape

The header is highly conditional:

- `UDF_READ_ONLY_BUILD` removes many mutating write/create/delete APIs from implementation but declarations are still organized around the full writable engine.
- `_X86_` enables assembly or external optimized helpers for directory index and bitmap operations.
- `UDF_LIMIT_DIR_SIZE` changes directory index frame size and layout.
- `UDF_CHECK_DISK_ALLOCATION`, `UDF_TRACK_ONDISK_ALLOCATION`, `UDF_TRACK_ALLOC_FREE_EXTENT`, `UDF_TRACK_EXTENT_TO_MAPPING`, `UDF_TRACK_FS_STRUCTURES`, and owner-tracking macros add diagnostics and source-location tracking.
- `_CONSOLE`, `UDF_DBG`, and `DBG` alter assertions, address checks, and inline-vs-macro wrappers.

## Integration Notes

This header is not a standalone public API. It assumes the full UDFS internal type universe from `udf.h` and included headers: `PVCB`, `PUDF_FILE_INFO`, `PUDF_DATALOC_INFO`, `PEXTENT_INFO`, `PEXTENT_MAP`, UDF descriptor structures, directory-index structures, memory allocation helpers, status macros, debug macros, and Windows kernel-style types.

The declarations show that `udf_info.cpp` is only one part of the `udf_info` module. Many declared functions are implemented in sibling files such as allocation, extent, mount, remap, and directory-tree sources.

## Risks and Review Points

- The many macro wrappers hide side effects, especially reference counting and allocation tracking. Callers must know whether a helper mutates parent open counts, Dloc link counts, or bitmap state.
- Generic bitmap macros evaluate arguments directly and are not type-safe; callers should avoid expressions with side effects.
- `UDFIsADirectory` can return true from either loaded state or on-disk FileIdent flags, which is convenient but can blur incomplete-open and fully-indexed-directory states.
- Reference macros assume `fi`, `fi->Dloc`, and optionally parent pointers are valid; they do not guard nulls.
- Directory index inline access returns `NULL` on out-of-range but relies on correct frame counts and `LastFrameCount`; corrupt or partially initialized indexes can break traversal assumptions.
- Build-configuration divergence is significant. Writable builds, read-only builds, x86 builds, and generic builds can exercise different code paths.
- `UDFGetFileAllocationSize` returns one logical block when no mapping exists, which may be a policy choice but can surprise callers expecting zero allocation for unmapped/empty objects.
- Stream and NT ACL support are revision-gated only by `maxUDFWriteRev`; callers still need to ensure the FE format and volume state support the requested operation.

## Testing Guidance

Tests using this header’s API surface should cover:

- Generic and x86 bitmap operations for aligned and unaligned bit ranges.
- Directory-index frame growth/truncation and index lookup at frame boundaries.
- Reference/dereference macro behavior with and without parent files.
- Allocation tracking macros in debug/tracking builds.
- Read-only build compilation, ensuring mutating paths are either unavailable or return write-protected status.
- Stream capability checks around UDF 1.50, 2.00, and later revisions.
- Verification cache init/read/write/forget/flush flows.
