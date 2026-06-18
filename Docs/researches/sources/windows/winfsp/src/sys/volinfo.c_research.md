# File Research: sources/windows/winfsp/src/sys/volinfo.c

## Purpose

`volinfo.c` implements volume information query and set handling for WinFsp filesystem volume devices. It answers static volume classes directly where possible, asks user mode for dynamic volume information when needed, and supports setting the filesystem label.

## Main Contents

Query helpers:

- `FspFsvolQueryFsAttributeInformation`
- `FspFsvolQueryFsDeviceInformation`
- `FspFsvolQueryFsFullSizeInformation`
- `FspFsvolQueryFsSectorSizeInformation`
- `FspFsvolQueryFsSizeInformation`
- `FspFsvolQueryFsVolumeInformation`
- `FspFsvolQueryVolumeInformation`
- `FspFsvolQueryVolumeInformationComplete`

Set helpers:

- `FspFsvolSetFsLabelInformation`
- `FspFsvolSetVolumeInformation`
- `FspFsvolSetVolumeInformationComplete`

Dispatch entries:

- `FspQueryVolumeInformation`
- `FspSetVolumeInformation`

## Query Behavior

`FspFsvolQueryVolumeInformation` handles these classes:

- `FileFsAttributeInformation`
- `FileFsDeviceInformation`
- `FileFsFullSizeInformation`
- `FileFsSectorSizeInformation`
- `FileFsSizeInformation`
- `FileFsVolumeInformation`

Static classes are answered directly from volume parameters. Dynamic classes use the `GETVOLUMEINFO` macro, which first tries cached volume information and returns `FSP_STATUS_IOQ_POST` when user mode must be queried.

If a user-mode query is required, the code creates a `FspFsctlTransactQueryVolumeInformationKind` request. Completion stores returned volume information in the fsvol device cache and formats the requested filesystem information class.

## Information Classes

`FspFsvolQueryFsAttributeInformation` fills:

- filesystem feature flags from volume parameters,
- maximum component length,
- filesystem name, optionally prefixed with `DRIVER_NAME` when the configured name begins with `-`, `/`, or `\`.

`FspFsvolQueryFsDeviceInformation` reports:

- `FILE_DEVICE_DISK`, intentionally required for `GetFileType` compatibility,
- device characteristics from the fsvol device object.

`FspFsvolQueryFsFullSizeInformation` and `FspFsvolQueryFsSizeInformation` compute allocation units from sector size and sectors per allocation unit.

`FspFsvolQueryFsSectorSizeInformation` reports logical and physical sector sizes equal to configured sector size and marks the device aligned with no seek penalty.

`FspFsvolQueryFsVolumeInformation` reports creation time, serial number, label length/text, and no object-ID support.

## Set Behavior

Only `FileFsLabelInformation` is supported.

`FspFsvolSetFsLabelInformation` has three modes:

- Preflight mode computes the extra request-buffer size from `VolumeLabelLength + sizeof(WCHAR)`.
- Request-fill mode writes the label into the request buffer and null-terminates it.
- Completion mode updates cached fsvol volume information from the response.

`FspFsvolSetVolumeInformation` validates the class, creates a `FspFsctlTransactSetVolumeInformationKind` request, fills it, and posts to IOQ.

`FspFsvolSetVolumeInformationComplete` propagates user-mode failure status or updates cached volume info and completes with zero information.

## Buffer Handling

- Each query helper checks fixed-structure space before writing.
- Variable-length names/labels may return `STATUS_BUFFER_OVERFLOW` after copying what fits.
- `IoStatus.Information` is always set to bytes written from the original system buffer.

## Notable Details

- `FileFsSectorSizeInformation` does not require dynamic user-mode volume info.
- Query/set dispatch accepts only `FspFsvolDeviceExtensionKind`.
- `FspFsvolSetVolumeInformationComplete` reads `Length` from `IrpSp->Parameters.SetFile.Length` even though this is a set-volume completion path; the label completion mode does not currently use that length, but it is a notable field mismatch.
