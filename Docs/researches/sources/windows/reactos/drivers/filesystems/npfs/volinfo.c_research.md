# File Research: sources/windows/reactos/drivers/filesystems/npfs/volinfo.c

## Purpose
Provides synthetic filesystem volume information for NPFS.

## Main Responsibilities
- `NpQueryFsVolumeInfo`:
  - Reports label `NamedPipe`.
  - `SupportsObjects = 0`.
- `NpQueryFsSizeInfo`:
  - Reports one sector per allocation unit and one byte per sector.
- `NpQueryFsDeviceInfo`:
  - Reports `FILE_DEVICE_NAMED_PIPE`.
- `NpQueryFsAttributeInfo`:
  - Reports filesystem name `NPFS`.
  - Sets `FILE_CASE_PRESERVED_NAMES`.
  - Uses max component name length `0xFFFFFFFF`.
- `NpQueryFsFullSizeInfo`:
  - Returns a zeroed full-size information structure.
- `NpCommonQueryVolumeInformation` dispatches by `FS_INFORMATION_CLASS`.
- `NpFsdQueryVolumeInformation` wraps dispatch in shared VCB locking.

## Important Interactions
- Registered as `IRP_MJ_QUERY_VOLUME_INFORMATION` in `main.c`.
- Does not inspect real pipe state; all outputs are static/synthetic.

## Risks / Review Notes
- Buffer length arithmetic is manual and unsigned.
- Size information is placeholder-like, but typical for a pseudo filesystem.
