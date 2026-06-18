# File Research: sources/windows/windows-driver-samples/filesys/cdfs/strucsup.c

## Purpose

Implements CDFS in-memory structure lifecycle: VCB initialization/deletion, FCB creation/initialization/teardown, CCB allocation, IRP context allocation/reuse, FCB table operations, TOC processing, file-lock creation, and audio-disc pseudo-volume support.

## Main Entry Points

- `CdInitializeVcb`
- `CdUpdateVcbFromVolDescriptor`
- `CdDeleteVcb`
- `CdCreateFcb`
- `CdInitializeFcbFromPathEntry`
- `CdInitializeFcbFromFileContext`
- `CdCreateCcb`
- `CdDeleteCcb`
- `CdCreateFileLock`
- `CdCreateIrpContext`
- `CdCleanupIrpContext`
- `CdInitializeStackIrpContext`
- `CdTeardownStructures`
- `CdLookupFcbTable`
- `CdGetNextFcb`
- `CdProcessToc`

## VCB Lifecycle

`CdInitializeVcb` zeroes the embedded VCB, initializes node type, notify synchronization, backup VPB, resources, mutexes, generic FCB table, target device reference, removable-media state, TOC fields, block factor, media change count, and initial mount reference counts. Audio-only media set audio/CD-XA state.

`CdUpdateVcbFromVolDescriptor` finalizes block geometry and creates internal FCBs. For data discs it creates the path-table stream, root directory index, and volume DASD FCB, initializes mappings and stream files, detects XA media, and sets sizes/attributes. For audio discs it creates pseudo path-table/root structures, synthesizes root directory size from track count, sets a hard-coded audio label, computes a TOC-derived serial, and exposes an ISO-like pseudo-root.

`CdDeleteVcb` frees the swap/current VPB as appropriate, dereferences the target device, frees XA and sector-cache state, removes the VCB from the global queue, deletes resources, frees TOC storage, uninitializes notify sync, and deletes the volume device object.

## FCB and CCB Lifecycle

`CdCreateFcb` looks up an existing FCB by file ID or allocates an index/path-table/data FCB, initializes common fields, MCB state, nonpaged FCB state, advanced header, and oplock state for data FCBs.

`CdInitializeFcbFromPathEntry` initializes directory FCBs from path-table entries, assigns stream offsets, ordinals, one-sector provisional sizes, initial allocation, directory attributes, parent linkage, references, and FCB-table insertion.

`CdInitializeFcbFromFileContext` initializes file FCBs from dirent enumeration results. It sets size/allocation, readonly/hidden attributes, creation time, XA/raw extent state, loads all extents into the MCB, marks the FCB initialized, links to the parent, increments parent references, and inserts into the FCB table.

`CdDeleteFcb` tears down per-stream contexts, MCBs, nonpaged state, prefix buffers, short-name prefix storage, file locks, oplocks, internal VCB pointers, and type-specific FCB allocations. System FCB deletion decrements VCB reference counts.

`CdCreateCcb` and `CdDeleteCcb` allocate, initialize, and free per-open CCBs, including any search-expression buffer.

## IRP Context Lifecycle

`CdCreateIrpContext` validates filesystem-device-object IRP patterns, reuses an IRP context from a private lookaside list when available, initializes operation fields, real device, VCB pointer, major/minor codes, and wait/force-post flags.

`CdCleanupIrpContext` restores thread context, frees allocated I/O context, and either returns the IRP context to the private lookaside list or frees it. For posted/retry work it clears the appropriate transient flags.

`CdInitializeStackIrpContext` builds a stack-resident IRP context for close processing from a lightweight context.

## Teardown and Tables

`CdTeardownStructures` walks from a starting FCB toward the root, deleting internal streams and unreferenced FCBs until it reaches a live node. It uses a top-level teardown flag to prevent recursion, removes prefixes, unlinks from parent queues, removes FCB-table entries, decrements parent references, and returns whether the starting FCB was removed.

`CdLookupFcbTable`, `CdGetNextFcb`, `CdFcbTableCompare`, `CdAllocateFcbTable`, and `CdDeallocateFcbTable` wrap the RTL generic table keyed by `FILE_ID`.

## TOC Processing

`CdProcessToc` reads CD TOC data using `IOCTL_CDROM_READ_TOC_EX` with fallback to `IOCTL_CDROM_READ_TOC`, validates returned track bounds, classifies audio/data tracks, hides the data track for CD+ style discs after audio lead-in, and updates the visible TOC length. `CdTocSerial` computes an audio-disc serial number from track addresses.

## Dependencies

This file is the central lifecycle provider for the rest of CDFS. It depends on allocation helpers, VPB spin locks, cache/internal stream creation, raw volume descriptor macros, dirent/path initialization, MCB allocation mapping, device I/O control helpers, FsRtl oplock/file-lock APIs, and global CDFS state.
