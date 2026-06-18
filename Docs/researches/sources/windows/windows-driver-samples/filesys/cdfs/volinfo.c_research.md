# File Research: sources/windows/windows-driver-samples/filesys/cdfs/volinfo.c

## Purpose

Implements `IRP_MJ_QUERY_VOLUME_INFORMATION` handling for CDFS.

## Main Entry Points

- `CdCommonQueryVolInfo`
- `CdQueryFsVolumeInfo`
- `CdQueryFsSizeInfo`
- `CdQueryFsDeviceInfo`
- `CdQueryFsAttributeInfo`
- `CdQueryFsSectorSizeInfo` for Windows 8+ builds

## Key Behavior

`CdCommonQueryVolInfo` decodes the file object, rejects unopened file objects, acquires the VCB shared, verifies the VCB, dispatches by `FsInformationClass`, records bytes written as original length minus remaining length, releases the VCB, and completes the IRP.

Supported classes are:

- `FileFsSizeInformation`
- `FileFsVolumeInformation`
- `FileFsDeviceInformation`
- `FileFsAttributeInformation`
- `FileFsSectorSizeInformation` when built for NTDDI Windows 8 or later

## Query Helpers

`CdQueryFsVolumeInfo` returns volume creation time from the volume DASD FCB, VPB serial number, `SupportsObjects = FALSE`, and as much of the VPB volume label as fits. It returns `STATUS_BUFFER_OVERFLOW` for truncated labels.

`CdQueryFsSizeInfo` reports total allocation units from the volume DASD allocation size, zero available units, one sector per allocation unit, and 2048-byte sectors.

`CdQueryFsDeviceInfo` reports target device characteristics and `FILE_DEVICE_CD_ROM`.

`CdQueryFsAttributeInfo` reports read-only CDFS attributes: case-sensitive search, read-only volume, and open-by-file-ID support. Joliet volumes also report `FILE_UNICODE_ON_DISK` and a shorter maximum component length. The filesystem name returned is `CDFS`, truncated with `STATUS_BUFFER_OVERFLOW` if needed.

`CdQueryFsSectorSizeInfo` delegates to `FsRtlGetSectorSizeInformation` on the real device and consumes the sector-size-info structure length on success.

## Dependencies

Uses CDFS file-object decoding, VCB verification, VPB volume metadata, volume DASD FCB sizing, VCB Joliet state, target/real device objects, and standard Windows filesystem information structures.
