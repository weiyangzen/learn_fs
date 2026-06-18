# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/vfat.h

## Purpose

`vfat.h` is the shared private header for the ReactOS VFAT/FATX filesystem driver. It defines on-disk FAT/FATX structures, core in-memory VCB/FCB/CCB/IRP-context structures, dispatch callback tables, flags, pool tags, inline helpers, and prototypes for the driver modules.

## On-Disk Structures and Constants

- Includes NT filesystem, disk, DOS, SEH, and section-attribute headers; KDBG builds include debugger support.
- Defines rounding macros for 32-bit and 64-bit alignment.
- Packed boot-sector structures:
  - `_BootSector` for FAT12/FAT16.
  - `_BootSector32` for FAT32.
  - `_BootSectorFatX` for FATX.
  - `_FsInfoSector` for FAT32 FSInfo.
- Directory/metadata structures:
  - FAT dirent and FATX dirent layouts.
  - Long filename slot layout.
  - OS/2-style EA file/set/header structures.
  - Union `DIR_ENTRY` for FAT/FATX code sharing.
- Defines FAT types `FAT12`, `FAT16`, `FAT32`, `FATX16`, and `FATX32`.
- Defines entry helper macros for deleted/end/volume/long entries across FAT and FATX.

## Core In-Memory State

- `FATINFO` stores parsed volume layout: sector/cluster sizes, FAT location/count/length, root/data starts, root cluster, cluster count, type, total sectors, volume ID/label, media kind, and FSInfo sector.
- `DEVICE_EXTENSION`/`VCB` stores:
  - directory and FAT resources
  - FCB list/hash table
  - volume and storage device objects
  - FAT stream file object
  - FATINFO and free-cluster state
  - volume/root FCBs
  - per-processor statistics
  - overflow request queue state
  - FAT operation callbacks
  - FATX/date mode
  - global volume-list entry
  - notify list/sync object
  - open-handle count
  - active/spare VPBs
  - directory-entry dispatch callbacks
- `VFAT_GLOBAL_DATA` stores global driver/device pointers, volume list, lookaside lists, fast I/O table, cache-manager callbacks, delayed-close state, close worker, and shutdown flag.
- `VFATFCB` stores common FCB header, section object pointers, resources, on-disk dirent, name strings/buffers, ref/open counts, parent/child/list/hash state, share access, file locks, last cluster cache, and delayed close context.
- `VFATCCB` stores current offset, flags, directory enumeration index, and search pattern.
- `VFAT_IRP_CONTEXT` stores the active IRP, device/VCB, flags, work item, stack location, major/minor function, file object, refcount, event, and priority boost.

## Inline Helpers and Flags

- VCB flags cover volume lock, dismount pending, FATX, system/page-file volume, good/usable state, dirty state, and pending dirty-clear state.
- FCB flags cover cache initialization, delete pending, FAT stream, page file, volume stream, dirty, delayed close, and KDBG cleanup/close markers.
- IRP-context flags cover can-wait, complete, queue, pending-returned, and deferred-write state.
- Inline wrappers call FAT/FATX directory dispatch operations through `DeviceExt->Dispatch`.
- `VfatMarkIrpContextForQueue()` converts an IRP context from complete to queued.
- `vfatFCBIsDirectory()`, `vfatFCBIsReadOnly()`, and `vfatVolumeIsFatX()` read common flags.
- `vfatReportChange()` emits directory-change notifications.
- `vfatAddToStat()` updates per-processor filesystem statistics.

## API Surface

The header declares cross-module functions for block I/O, cleanup/close/create, directory enumeration and date conversion, dirent access, directory writes and moves, EA setting, fast I/O callbacks, FAT cluster operations and dirty-bit operations, FCB lifecycle/table lookup, file information, flush, fsctl, driver entry, common dispatch/queue helpers, PnP, read/write, shutdown, string helpers, and volume query/set.

## Research Notes

`vfat.h` is the best map of module boundaries. It also reveals architectural constraints that appear throughout the C files: FATX behavior is selected through callbacks and flags, FAT12/16 root directories are special, volume lifecycle depends on VPB swapping, and most request deferral is carried by `VFAT_IRP_CONTEXT`.
