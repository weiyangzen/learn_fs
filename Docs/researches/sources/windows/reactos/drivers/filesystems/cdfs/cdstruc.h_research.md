# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cdstruc.h

## Purpose

`cdstruc.h` defines the core in-memory CDFS data model: global filesystem state, mounted volume state, file/control blocks, per-open context, request context, enumeration contexts, RIFF/audio headers, file IDs, and optional telemetry state.

## Key Contents

- Design commentary:
  - Describes `CdData`, filesystem device objects, volume device objects, VCB queue, FCB table, root/index/file tree, prefix tables, file-object context pointers, and synchronization order.
  - Establishes normal lock ordering: CdData, VCB, FCB, with special FCB tree ordering rules.

- Allocation/name/prefix primitives:
  - `CD_MCB` and `CD_MCB_ENTRY` map file offsets to disk offsets and support interleaved/raw sector layouts.
  - `CD_NAME` stores filename and version string.
  - `NAME_LINK` and `PREFIX_ENTRY` support exact-case and ignore-case prefix splay trees.

- `CD_DATA`
  - Global filesystem record.
  - Holds driver/device pointers, VCB queue, IRP context cache, async/delayed close queues, close worker item, global mutex/resource, and cache-manager callbacks.
  - ReactOS adds `HddFileSystemDeviceObject`.

- `CDROM_TOC_LARGE`
  - Larger TOC representation supporting up to `0xAA` track entries.

- Sector cache:
  - `CD_SECTOR_CACHE_CHUNK`
  - `CD_SEC_CACHE_CHUNKS`
  - `CD_SEC_CHUNK_BLOCKS`

- `VCB`
  - Mounted volume control block with VPB, target device, volume lock file object, queue links, state/condition, cleanup/reference counts, special FCBs, session/descriptor offsets, XA sector cache, resources, mutex, notify state, logical block geometry, FCB table, TOC data, media-change count, transfer limits, swap VPB, directory sector cache, and optional telemetry correlation ID.
  - Conditions:
    - `VcbNotMounted`
    - `VcbMountInProgress`
    - `VcbMounted`
    - `VcbInvalid`
    - `VcbDismountInProgress`
  - State flags include ISO/HSG/Joliet, locked, removable, CD-XA, audio disk, notify remount, VPB detached, shutdown, and dismounted.

- `VOLUME_DEVICE_OBJECT`
  - Embeds an I/O `DEVICE_OBJECT`, overflow queue accounting/lock, and the filesystem `VCB`.

- FCB family:
  - `FCB_DATA` contains oplock state on pre-Win8 and optional file-lock pointer.
  - `FCB_INDEX` contains internal stream file object, stream offset, child FCB queue, path-table ordinal/child offsets, and prefix roots.
  - `FCB_NONPAGED` contains section object pointers, FCB resource, FCB mutex, and advanced-header mutex.
  - `FCB` embeds `FSRTL_ADVANCED_FCB_HEADER`, VCB/parent links, file ID, reference/cleanup counts, state, attributes, XA metadata, recursive lock state, nonpaged block, share access, MCB, prefix entries, creation time, and either data or index-specific payload.
  - FCB state flags identify initialized/table membership and raw-sector file types.

- `CCB`
  - Per-handle state with flags, FCB pointer, directory enumeration offset, and search expression.
  - Flags include open-by-ID, ignore-case, versioned open, dismount-on-close, extended DASD I/O, and enumeration state flags.

- `IRP_CONTEXT`
  - Per-originating-IRP state with original IRP, VCB, exception status, flags, real device, I/O or teardown context, top-level context, major/minor function, thread context, and work item.
  - Flags track waitability, posting, top-level ownership, FSP context, teardown, allocated I/O, popup disable, verify forcing, and create-name properties.

- `IRP_CONTEXT_LITE`
  - Compact delayed-close payload containing FCB, list link, user-reference count, and real device.

- `CD_IO_CONTEXT`
  - Tracks async/sync noncached I/O, master IRP, request count, status, resource release data, or sync event.

- `THREAD_CONTEXT`
  - Stack-resident top-level CDFS context with signature, saved top-level IRP, and top-level IRP context pointer.

- Enumeration structures:
  - `PATH_ENUM_CONTEXT`
  - `PATH_ENTRY`
  - `COMPOUND_PATH_ENTRY`
  - `DIRENT_ENUM_CONTEXT`
  - `DIRENT`
  - `COMPOUND_DIRENT`
  - `FILE_ENUM_CONTEXT`

- Synthetic file headers:
  - `RIFF_HEADER`
  - `AUDIO_PLAY_HEADER`

- File ID macros:
  - Encode directory bit in `LowPart` high bit.
  - Store parent/path-table offset in `HighPart`.
  - Store dirent offset in `LowPart`.
  - Provide helpers for query/set/directory marking and constructing IDs from parent+dirent.

- Optional `CDFS_TELEMETRY_DATA_CONTEXT`
  - Tracks missed telemetry points, periodic telemetry timing, volume GUID, optional debug interval, and filesystem statistics.

## Dependencies and Interactions

- Used by `cddata.h` assertions, `cdprocs.h` prototypes/macros, close/cleanup logic, create/path/name/dirent code, and VCB teardown.
- CCB/FCB/VCB count fields are directly manipulated by macros in `cdprocs.h`.
- `IRP_CONTEXT` fields are central to dispatch, exception processing, posting, cleanup, close, and verify paths.
- `VCB` sector cache and TOC fields support mount, read, XA/audio, and directory enumeration behavior.

## Behavioral Notes

- This header is the best map of CDFS lifetime rules: handles affect cleanup counts, object references affect teardown, and residual references keep core volume structures alive.
- Synchronization rules are explicitly documented and are essential because close/cleanup paths can run recursively or from worker threads.
- File IDs deliberately make directory parent lookup efficient by using a zero dirent offset plus a directory marker bit.
