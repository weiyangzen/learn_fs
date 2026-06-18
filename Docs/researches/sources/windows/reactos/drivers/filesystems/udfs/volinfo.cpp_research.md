# File Research: sources/windows/reactos/drivers/filesystems/udfs/volinfo.cpp

This file implements UDF query/set volume information dispatch paths.

Key functions:
- `UDFQueryVolInfo`
  - Top-level IRP wrapper for `IRP_MJ_QUERY_VOLUME_INFORMATION`.
  - Enters filesystem context, allocates IRP context, calls `UDFCommonQueryVolInfo`, handles exceptions, completes or posts.
- `UDFCommonQueryVolInfo`
  - Reads query class and output length.
  - Optionally checks access under `UDF_ENABLE_SECURITY`.
  - Zeroes the system buffer.
  - Dispatches to volume, size, device, attribute, and full-size query helpers.
  - Acquires `VCBResource` shared for label-copying in `FileFsVolumeInformation`.
- `UDFQueryFsVolumeInfo`
  - Returns volume creation time, physical serial number, `SupportsObjects = FALSE`, and volume label with overflow handling.
- `UDFQueryFsSizeInfo`
  - Returns total/free allocation units, sectors per allocation unit, and bytes per sector.
  - Recomputes space when `BitmapModified` is set and updates `LowFreeSpace`.
- `UDFQueryFsFullSizeInfo`
  - Same space model as size info, filling caller and actual available units.
- `UDFQueryFsDeviceInfo`
  - Returns target device type and characteristics.
  - Clears read-only/write-once characteristics for non-CD/DVD target devices.
- `UDFQueryFsAttributeInfo`
  - Reports case sensitivity/preservation, named streams when supported, sparse-file support, optional persistent ACLs, read-only volume state, and Unicode-on-disk.
  - Chooses a filesystem title based on device type, raw/blank state, CDR mode, and media class.
- `UDFSetVolInfo`
  - Top-level wrapper for `IRP_MJ_SET_VOLUME_INFORMATION` when not read-only build.
- `UDFCommonSetVolInfo`
  - Allows only volume-label changes, rejects non-volume objects and raw disks, checks security when enabled, and posts when VCB acquisition cannot block.
- `UDFSetLabelInfo`
  - Validates label length, reallocates `Vcb->VolIdent`, copies the new label, null-terminates it, and marks the volume modified.

Notable design points:
- Free-space values are cached in the VCB and refreshed only when bitmap state says they are stale.
- The filesystem name returned to callers is media-sensitive rather than always a single `UDF` string.
- Label setting updates in-memory state and marks modified; actual persistence is delegated to later flush/update paths.
