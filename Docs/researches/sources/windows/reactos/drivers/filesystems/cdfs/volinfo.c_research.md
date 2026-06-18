# File Research: sources/windows/reactos/drivers/filesystems/cdfs/volinfo.c

Implements `IRP_MJ_QUERY_VOLUME_INFORMATION` support for CDFS.

Key entry points:
- `CdCommonQueryVolInfo()` decodes the file object, acquires the VCB shared, verifies the VCB, dispatches by filesystem information class, records bytes returned, and completes the IRP.
- `CdQueryFsVolumeInfo()` returns creation time, serial number, object-support flag, and volume label.
- `CdQueryFsSizeInfo()` returns total allocation units, zero available units, one sector per allocation unit, and sector size.
- `CdQueryFsDeviceInfo()` returns target-device characteristics and device type.
- `CdQueryFsAttributeInfo()` returns filesystem attributes, component-name limits, and the filesystem name `CDFS`.
- `CdQueryFsSectorSizeInfo()` returns sector-size information through `FsRtlGetSectorSizeInformation()` when available for the build target.

Core mechanics:
- ReactOS zeroes the caller's system buffer before filling query output.
- Volume labels are copied partially with `STATUS_BUFFER_OVERFLOW` if the buffer is too small.
- File system attributes always include case-sensitive search, read-only volume, and open-by-file-ID support.
- Joliet volumes add `FILE_UNICODE_ON_DISK` and use a 110-character maximum component length; non-Joliet uses 221.
- Size information derives total allocation units from the volume DASD FCB allocation size.

Important invariants:
- Query volume rejects unopened file objects.
- All query classes run after `CdVerifyVcb()`.
- Returned `IoStatus.Information` is computed from the original length minus remaining length.

Filesystem relevance:
- Exposes CDFS volume metadata to user mode and system callers.
- Reports CDFS as read-only and distinguishes Joliet Unicode-on-disk capability.

Notable risks:
- Helper routines subtract fixed structure sizes from `Length`; callers rely on the I/O manager and dispatch path to provide adequate fixed-size buffers.
- `FileFsSectorSizeInformation` is compiled only for NTDDI targets that define the class.
