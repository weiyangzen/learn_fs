# File Research: sources/windows/windows-driver-samples/filesys/fastfat/volinfo.c

## Role

`volinfo.c` implements FastFAT query and set volume information dispatch paths for `IRP_MJ_QUERY_VOLUME_INFORMATION` and `IRP_MJ_SET_VOLUME_INFORMATION`.

## Key Routines

- `FatFsdQueryVolumeInformation`: top-level dispatch wrapper for query volume information. It enters the filesystem, creates an IRP context, calls the common query routine, and routes exceptions through FastFAT exception handling.
- `FatFsdSetVolumeInformation`: equivalent wrapper for set volume information.
- `FatCommonQueryVolumeInfo`: decodes the file object, verifies the root DCB, dispatches by `FS_INFORMATION_CLASS`, acquires the VCB when copying mutable volume label state, and completes the IRP.
- `FatCommonSetVolumeInfo`: requires a `UserVolumeOpen`, acquires the VCB exclusively, verifies the root DCB, and currently supports `FileFsLabelInformation`.
- `FatQueryFsVolumeInfo`: returns serial number, object support flag, and volume label with buffer-overflow-aware truncation.
- `FatQueryFsSizeInfo`: returns total/free clusters and sector/cluster geometry.
- `FatQueryFsDeviceInfo`: returns disk device type and target device characteristics.
- `FatQueryFsAttributeInfo`: returns FAT filesystem attributes, maximum component length, read-only flag, and filesystem name `FAT` or `FAT32`.
- `FatQueryFsFullSizeInfo`: returns caller and actual available allocation units, matching FAT’s global free-space view.
- `FatSetFsLabelInfo`: validates, normalizes, creates, updates, or deletes the root-directory volume label dirent and mirrors the label into the VPB.
- `FatQueryFsSectorSizeInfo`: on supported builds, calls `FsRtlGetSectorSizeInformation` for physical/logical sector size data.

## Important Mechanics

Setting a volume label is write-through and carefully ordered. The code updates the on-disk volume label dirent first, unpins/flushes repinned BCBs to surface I/O errors, and only then changes the VPB label. This avoids a window where the in-memory label claims a change that failed on disk.

Label validation converts Unicode to uppercase OEM, enforces FAT’s 11-character volume label limit, rejects illegal FAT characters and dots, handles DBCS lead bytes, strips trailing spaces, and maps an initial `0xe5` byte to FAT’s special escaped value.

Query paths mostly read stable VCB/BPB/allocation fields, but volume label queries acquire the VCB shared because the VPB label can change.

## Dependencies And Coupling

This file depends on IRP stack decoding, FastFAT file-object decoding, VCB locking, root DCB verification, BPB/allocation support, VPB label fields, directory-entry creation, pinned BCB writeback, and Windows `FILE_FS_*` information structures.
