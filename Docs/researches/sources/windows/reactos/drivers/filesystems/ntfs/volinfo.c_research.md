# File Research: sources/windows/reactos/drivers/filesystems/ntfs/volinfo.c

## Purpose

`volinfo.c` implements NTFS free-space accounting, cluster allocation from `$Bitmap`, query-volume-information IRPs, and the unsupported set-volume-information path.

## Cluster Bitmap Functions

`NtfsGetFreeClusters`

- Allocates a file-record buffer and reads system file `$Bitmap`.
- Finds `$Bitmap::$DATA`.
- Allocates a sector-rounded bitmap buffer.
- Reads the bitmap attribute sector by sector.
- Initializes an `RTL_BITMAP` over `DeviceExt->NtfsInfo.ClusterCount`.
- Returns `RtlNumberOfClearBits`.
- Returns zero on allocation, read, or attribute lookup failures.

`NtfsAllocateClusters`

- Reads `$Bitmap::$DATA`.
- Caps bitmap data size to 32-bit addressable length.
- Builds an `RTL_BITMAP` over volume clusters.
- Fails with `STATUS_DISK_FULL` if clear-bit count is below requested clusters.
- Tries to allocate one contiguous clear run at or after `FirstDesiredCluster`.
- If that fails, returns the next forward clear run or the longest clear run.
- Writes the modified bitmap attribute back through `WriteAttribute`.
- Does not yet observe the NTFS MFT reservation zone.

## Query Volume Information

`NtfsGetFsVolumeInformation`

- Validates output buffer size.
- Returns VPB serial number and volume label.
- Fills dummy volume creation time of zero and `SupportsObjects = FALSE`.

`NtfsGetFsAttributeInformation`

- Reports:
  - `FILE_CASE_PRESERVED_NAMES`
  - `FILE_UNICODE_ON_DISK`
  - `FILE_READ_ONLY_VOLUME`
- Maximum component name length: 255.
- Filesystem name: `NTFS`.

`NtfsGetFsSizeInformation`

- Returns free clusters via `NtfsGetFreeClusters`.
- Returns total clusters, sectors per allocation unit, and bytes per sector from `NtfsInfo`.

`NtfsGetFsDeviceInformation`

- Reports `FILE_DEVICE_DISK` and the mounted device object's characteristics.

`NtfsQueryVolumeInformation`

- Acquires `DeviceExt->DirResource` shared, or queues if it cannot wait.
- Zeroes the caller's system buffer.
- Dispatches `FileFsVolumeInformation`, `FileFsAttributeInformation`, `FileFsSizeInformation`, and `FileFsDeviceInformation`.
- Releases the resource and sets `IoStatus.Information` from consumed buffer length on success.

`NtfsSetVolumeInformation`

- Always returns `STATUS_NOT_SUPPORTED`.

## Integration

- Uses MFT and attribute helpers from `mft.c` to read/write `$Bitmap`.
- Supplies `NtfsAllocateClusters` to nonresident attribute growth in `mft.c`.
- Uses `NtfsMarkIrpContextForQueue` from `ntfs.h` when query-volume work cannot acquire the volume resource immediately.

## Notable Behavior and Risks

- Free-space counting is explicitly noted as underoptimized.
- `$Bitmap` reads are manually sector-looped in `NtfsGetFreeClusters`.
- Cluster allocation rewrites the whole bitmap attribute after setting bits.
- `NtfsAllocateClusters` checks enough total free clusters before choosing a run, but may return a smaller run than requested when no contiguous run exists.
- The reported filesystem attributes always include `FILE_READ_ONLY_VOLUME`, even though experimental write support can be enabled globally.
- Set-volume information is entirely unsupported.
