# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cdstruc.h

## Purpose

`cdstruc.h` defines the major in-memory CDFS data structures: global filesystem state, mounted volume state, FCB/CCB/IRP context state, enumeration contexts, normalized dirent/path entries, XA/audio headers, file ID encoding, and optional telemetry state. It also documents the CDFS object graph and locking hierarchy.

## Architecture Notes

The header describes:

- `CdData` owns the filesystem device object and VCB queue.
- Each mounted or previously mounted volume has a VCB embedded in a volume device object.
- Each VCB owns an FCB table indexed by `FILE_ID`.
- Directory FCBs own child FCB lists and prefix tables.
- Open-by-ID paths may create detached subtrees.
- File objects point to FCB and optional CCB.
- Stream file objects point directly to FCBs for cached internal streams.

## Synchronization Model

The documented lock order is central:

- CdData resource protects mount/dismount and VCB queue.
- VCB resource protects open/close state.
- VCB file resource synchronizes file operations across the volume.
- FCB nonpaged resource protects open/close for an FCB.
- VCB mutex protects FCB table and reference/open counts.
- FCB mutex protects miscellaneous FCB fields and supports recursive locking.
- Multiple FCB locks are acquired leaf-to-root.
- Cleanup only holds locks long enough to adjust counts/share/lock state.

## Major Structures

- `CD_MCB` / `CD_MCB_ENTRY`
  - Logical stream-to-disc allocation mappings.
  - Stores file offset, disc offset, byte count, and interleave geometry.

- `CD_NAME`, `NAME_LINK`, `PREFIX_ENTRY`
  - Normalized CDFS names, version strings, splay-tree links, and prefix entries.

- `CD_DATA`
  - Global driver state: driver object, filesystem device object, VCB queue, IRP context cache, async/delayed close queues, global resource, cache-manager callbacks, close work item.

- `CDROM_TOC_LARGE`
  - Extended TOC container supporting up to `0xAA` track entries.

- `VCB`
  - Mounted volume state: VPB, target device, lock file object, condition/state flags, cleanup/reference counts, root/path/DASD FCBs, volume descriptor offsets, XA sector cache, synchronization resources, block geometry, FCB table, TOC data, transfer limits, swap VPB, directory pre-cache, optional telemetry correlation ID.

- `VOLUME_DEVICE_OBJECT`
  - Kernel `DEVICE_OBJECT` plus posted request accounting/overflow queue and embedded `VCB`.

- `FCB_DATA`, `FCB_INDEX`, `FCB_NONPAGED`, `FCB`
  - Data-file extension with oplock/file-lock state.
  - Index/path-table extension with stream file object, stream offset, child list, ordinals, child path-table offsets, and prefix trees.
  - Nonpaged section/resource/mutex state.
  - Common FCB stores advanced header, VCB/parent links, file ID, counts, flags, attributes, XA metadata, locks, share access, MCB, prefix entries, creation time, and type-specific union.

- `CCB`
  - Per-file-object context with flags, FCB pointer, directory enumeration offset, and search expression.

- `IRP_CONTEXT`
  - Per-originating-IRP state: IRP, VCB, exception status, flags, real device, I/O context or teardown FCB pointer, top-level context, major/minor function, thread context, work item.

- `IRP_CONTEXT_LITE`
  - Minimal delayed-close context with FCB, list link, user reference count, and real device.

- `CD_IO_CONTEXT`
  - Tracks multi-IRP or synchronous noncached I/O completion state.

- `THREAD_CONTEXT`
  - Stack-resident top-level CDFS context with signature, saved previous top-level IRP, and top-level IRP context pointer.

- `PATH_ENUM_CONTEXT`, `PATH_ENTRY`, `COMPOUND_PATH_ENTRY`
  - Path-table enumeration and normalized path entry state, including cache BCBs, spanning-view buffers, ordinals, parent ordinals, disc offsets, names, and cleanup flags.

- `DIRENT_ENUM_CONTEXT`, `DIRENT`, `COMPOUND_DIRENT`, `FILE_ENUM_CONTEXT`
  - Directory stream enumeration and normalized dirent state.
  - `FILE_ENUM_CONTEXT` keeps prior/initial/current dirents for multi-dirent file handling and short-name generation.

- `RIFF_HEADER`, `AUDIO_PLAY_HEADER`
  - In-memory layouts for headers prepended to XA and audio pseudo files.

- Optional `CDFS_TELEMETRY_DATA_CONTEXT`
  - Tracks missed telemetry due to stack limits, periodic timing, volume GUID, and filesystem statistics.

## File ID Encoding

The `FILE_ID` macros encode:

- Directories:
  - `HighPart`: path-table offset.
  - `LowPart`: directory flag bit set, dirent offset treated as zero.

- Files:
  - `HighPart`: parent directory path-table offset.
  - `LowPart`: dirent byte offset in parent directory.

Macros query/set dirent offset, path-table offset, directory bit, and derive IDs from parent/dirent pairs.

## Integration

This header is included through `cdprocs.h` and underpins all modules. Allocation uses `CD_MCB`; cache and MM use FCB nonpaged section state; create/close/cleanup use FCB/CCB/VCB counts; directory and path support use enum contexts; read paths use XA/audio metadata and I/O contexts.

## Risk Notes

- Structure field ordering is ABI-sensitive for kernel, FSRTL, cache manager, and debugging assumptions.
- The unioned FCB layout requires correct `NodeTypeCode` and size selection.
- Reference and cleanup counts are spread across FCB and VCB and protected by different locks; pairing errors cause leaks or premature teardown.
- Directory/path enumeration contexts hold pinned cache data and optional pool buffers, so cleanup macros must match initialization paths.
