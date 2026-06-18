# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/volume.c

## Purpose

`volume.c` implements `IRP_MJ_QUERY_VOLUME_INFORMATION` and `IRP_MJ_SET_VOLUME_INFORMATION` for VFAT. It reports volume label/serial/creation time, filesystem attributes, allocation size/free space, device characteristics, and supports setting the volume label.

## Query Helpers

- `FsdGetFsVolumeInformation()` fills `FILE_FS_VOLUME_INFORMATION` from the VPB serial/label and volume FCB creation time. FATX and FAT timestamp fields are handled separately.
- `FsdGetFsAttributeInformation()` reports the filesystem name as `FAT`, `FAT32`, or `FATX`; sets `FILE_CASE_PRESERVED_NAMES | FILE_UNICODE_ON_DISK`; and reports maximum component length 255.
- `FsdGetFsSizeInformation()` calls `CountAvailableClusters()` and fills total clusters, free clusters, sectors per cluster, and bytes per sector.
- `FsdGetFsDeviceInformation()` reports `FILE_DEVICE_DISK` and the mounted device characteristics.
- `FsdGetFsFullSizeInformation()` reports caller/actual available clusters, total clusters, sectors per allocation unit, and bytes per sector.

## Label Setting

- `FsdSetFsLabelInformation()` validates label length against the VPB buffer and FAT/FATX on-disk limits.
- Converts the Unicode label to OEM bytes.
- Builds a volume-label dirent:
  - FATX: up to 42 characters, `_A_VOLID`.
  - FAT: up to 11 characters across filename/ext fields, `_A_VOLID`.
- Opens and initializes the root FCB cache.
- Scans root entries with `CcPinRead()` for an existing volume-label entry.
- Updates an existing label in place or finds one free dirent slot and writes a new label entry.
- Marks pinned data dirty and updates the VPB label in memory.

## Dispatch Behavior

- `VfatQueryVolumeInformation()` acquires `DirResource` shared, zeroes the output buffer, dispatches by `FS_INFORMATION_CLASS`, releases the resource, and reports bytes written.
- `VfatSetVolumeInformation()` acquires `DirResource` exclusive and currently supports only `FileFsLabelInformation`.

## Research Notes

Label mutation edits the root directory directly through the cache manager. Query paths rely on VPB state populated during mount, while size/free-space queries force cluster counting through FAT-layer support.
