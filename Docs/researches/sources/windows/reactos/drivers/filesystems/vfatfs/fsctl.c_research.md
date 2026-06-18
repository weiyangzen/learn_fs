# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fsctl.c

## Purpose

`fsctl.c` implements VFAT file-system-control handling: volume recognition, mount, verify, dirty-state queries/updates, lock/unlock, dismount, retrieval pointers, and filesystem statistics. It is the mount-time bridge between raw block devices, parsed FAT/FATX layout metadata, cache-manager stream setup, and the live VCB/VPB state used by the rest of `vfatfs`.

## Main Runtime Flow

- `VfatHasFileSystem()` probes a target block device with `IOCTL_DISK_GET_DRIVE_GEOMETRY` and, for fixed/removable media, `IOCTL_DISK_GET_PARTITION_INFO`; it then reads sector zero and validates FAT12/FAT16/FAT32 boot-sector fields or, if ordinary FAT recognition fails on a valid partition, FATX16/FATX32 Xbox boot-sector fields.
- FAT recognition computes `FATINFO`: FAT start/count/length, root/data starts, bytes and sectors per cluster, cluster count, FAT type, root cluster, volume ID/label, media kind, total sectors, and FAT32 FSInfo sector.
- `ReadVolumeLabel()` scans root-directory entries either through the root FCB/cache path after mount or by direct disk reads during verify. It supports both FAT volume-label entries and FATX volume-label entries.
- `VfatMount()` validates that the mount request targets the global file system device, recognizes the media, creates the per-volume filesystem device, allocates a hash table sized by FAT type, initializes VCB state/resources/statistics, binds the VPB, sets FAT-specific callback functions, creates stream FCBs for the FAT and volume, initializes the FAT cache map, counts free clusters, reads label/serial, marks clean volumes dirty, initializes notifications, and emits `FSRTL_VOLUME_MOUNT`.
- `VfatVerify()` rechecks media change state and compares the newly parsed `FATINFO` and label against the mounted VPB. It returns `STATUS_WRONG_VOLUME` when the disk no longer matches.
- `VfatFileSystemControl()` dispatches `IRP_MN_MOUNT_VOLUME`, `IRP_MN_VERIFY_VOLUME`, and user/kernel FSCTLs.

## FSCTL Support

- Implemented:
  - `FSCTL_GET_RETRIEVAL_POINTERS`: walks the file cluster chain and returns extents in `RETRIEVAL_POINTERS_BUFFER`.
  - `FSCTL_IS_VOLUME_DIRTY`: reports `VOLUME_IS_DIRTY` from VCB/volume FCB flags.
  - `FSCTL_MARK_VOLUME_DIRTY`: sets the on-disk dirty bit when needed and clears the pending clean-on-dismount flag.
  - `FSCTL_LOCK_VOLUME` and `FSCTL_UNLOCK_VOLUME`: require the volume FCB, coordinate VCB/VPB lock flags, flush on lock, and emit volume events.
  - `FSCTL_DISMOUNT_VOLUME`: requires a locked non-system volume, flushes, clears dirty state when possible, destroys FCBs, marks dismount pending, and clears VCB usability.
  - `FSCTL_FILESYSTEM_GET_STATISTICS`: returns per-processor FAT statistics.
- Stubbed as invalid requests:
  - `FSCTL_GET_VOLUME_BITMAP`
  - `FSCTL_MOVE_FILE`

## Important Details

- FAT12/16 root directories are treated specially because they are fixed regions rather than normal cluster chains.
- FATX detection is attempted only after ordinary FAT detection fails and partition information is considered valid.
- Dirty-bit handling marks a clean mounted volume dirty immediately and records `VCB_CLEAR_DIRTY` so clean lock/dismount/shutdown paths can clear the bit later.
- Volume locking normally requires `OpenHandleCount == 1`, but there is a narrow boot-volume hack allowing autochk-era locking when only a small number of directory handles are open.
- Mount failure cleanup tears down cache maps, stream file objects, FCBs, statistics, spare VPB, and the partially created device.

## Research Notes

This file is central to the VFAT lifecycle. When studying correctness, focus on recognition field validation, VPB ownership transitions, dirty-bit ordering, and the lock/dismount relationship with `misc.c` dismount cleanup and `shutdown.c` clean shutdown.
