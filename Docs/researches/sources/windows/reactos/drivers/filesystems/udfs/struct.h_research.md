# File Research: sources/windows/reactos/drivers/filesystems/udfs/struct.h

## Purpose

`struct.h` defines the core in-memory UDFS driver structures and flag constants used by dispatch, cache, FCB/CCB lifecycle, VCB integration, delayed close, statistics, and device extensions.

## Main Structures

- `UDFIdentifier`
  - common node signature and size header used by UDFS-owned allocations
- `UDFObjectName`
  - stores absolute pathname metadata for an FCB
- `UDFCCB`
  - per-open context control block
  - links into an FCB’s CCB list
  - stores file object, open/search flags, current directory index, optional search pattern, hashes, tree length, and previously granted access
- `UDFNTRequiredFCB`
  - nonpaged NT-required FCB portion
  - starts with `FSRTL_COMMON_FCB_HEADER`
  - owns section object pointers, file locks, main/paging resources, timestamps, share-access state, security descriptor, lazy-writer tracking, and close-thread state
- `UDFFCB`
  - UDFS logical file control block
  - references `UDFNTRequiredFCB`, `UDF_FILE_INFO`, owning VCB, CCB list, object name, parent FCB, delayed-close context, reference/open counts, and state flags
- `FILTER_DEV_EXTENSION` and `UDFFS_DEV_EXTENSION`
  - small device-extension node-signature structures
- `UDFIrpContext`
  - per-IRP dispatch context used by common FSD/FSP routines
  - carries IRP, major/minor function, target device, saved exception code, work item, transition buffer/MDL, and request flags
- `UDFIrpContextLite`
  - reduced delayed-close queue item
- `UDFEjectWaitContext`
  - state for asynchronous removable-media/eject handling
- `UDFBGWriteContext`
  - background write work item context
- `FILE_SYSTEM_STATISTICS`
  - UDFS statistics wrapper with FAT-compatible statistics payload and cache-line padding
- `UDFFileIDCacheItem`
  - file ID to full-name cache entry

## Flag Groups

The header defines central flag bitmasks for:

- CCB open state, cleanup state, search semantics, wildcard handling, access mode, delete-on-close, and validity
- NT-required FCB descriptor modification/list/deleted/valid state
- FCB file type/state, mapped data, delayed close, deletion, modified/accessed state, and allocation provenance
- IRP context blocking, write-through, exception, async, top-level, popup, flush, read-only, resource-acquired, forced-post, and buffer-lock state
- flush input/output flags and background-writer limits

## Integration

`struct.h` includes `Include/platform.h`, `udf_info/udf_rel.h`, and `Include/udf_common.h`, so it is a bridge between OS-specific driver state and the lower UDF metadata library. Most files in the UDFS driver depend on the FCB/CCB/VCB/IRP structures declared here.

## Notable Details

- The NT-required FCB is allocated separately rather than embedded in `UDFFCB`, with comments pointing to hard-link/symbolic-link complications.
- `UDFNTRequiredFCB.SecurityDesc` is the cached security descriptor manipulated by `secursup.cpp`.
- Several structures are documented as zone/nonpaged aligned, and flags distinguish zone-allocated from non-zone allocations.
- The `FILE_SYSTEM_STATISTICS` padding assumes the payload is no larger than a 64-byte multiple; changes to embedded structures would need care.
