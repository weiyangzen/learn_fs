# File Research: sources/windows/dokany/sys/volume.c

## Purpose
Handles `IRP_MJ_QUERY_VOLUME_INFORMATION` and `IRP_MJ_SET_VOLUME_INFORMATION` for Dokany volumes, including early default responses before user-mode event processing is ready.

## Main Behavior
- `DokanDispatchQueryVolumeInformation()` validates the VCB and file object, logs the requested `FS_INFORMATION_CLASS`, then handles volume information classes.
- Before `Vcb->HasEventWait` is true, it returns hard-coded defaults for selected queries:
  - `FileFsVolumeInformation`: zero creation time, fixed serial number, default `VOLUME_LABEL`.
  - `FileFsSizeInformation`: 1 GiB total, 512 MiB free, default allocation unit and sector size.
  - `FileFsAttributeInformation`: hard links, case-sensitive search, preserved names, `NTFS` filesystem name.
  - `FileFsFullSizeInformation`: same default space values with caller/actual available fields.
- `FileFsDeviceInformation` is always answered in-kernel from DCB device type and characteristics.
- Once user-mode processing is available, selected query classes are packaged into an `EVENT_CONTEXT` and registered as pending IRPs for user-mode completion.
- `DokanCompleteQueryVolumeInformation()` validates returned buffer size, optionally adds `FILE_READ_ONLY_VOLUME`, overrides volume label from `Dcb->VolumeLabel`, copies user-mode data to the IRP output buffer, and sets final status/information.
- `DokanDispatchSetVolumeInformation()` supports `FileFsLabelInformation` by replacing `Dcb->VolumeLabel` under the DCB resource lock.

## Integration Points
- Dispatched from `dispatch.c` for query volume IRPs and completed from `event.c`.
- Uses `AllocateEventContext()` and `DokanRegisterPendingIrp()` for user-mode round trips.
- Uses `DokanGetFsInformationClassStr()` for logging and `PREPARE_OUTPUT` for structured output preparation.
- Reads and updates DCB/VCB fields including `HasEventWait`, `DeviceType`, `DeviceCharacteristics`, `VolumeLabel`, and read-only device flags.
- User-mode volume callbacks live in the Dokany library side and fill `EVENT_INFORMATION`.

## Risks and Notes
- Early mount-time defaults are intentional compatibility behavior for filter drivers issuing queries before user-mode worker threads are available.
- `DokanCompleteQueryVolumeInformation()` rejects returned data when `EventInfo->BufferLength` exceeds the IRP buffer length, using `STATUS_INSUFFICIENT_RESOURCES`.
- Volume-label override truncates to caller buffer capacity and updates `EventInfo->BufferLength` to the copied label structure size.
- `FileFsLabelInformation` allocation failure returns while holding the DCB resource lock; that path should be reviewed if modifying label handling.
- Only volume label setting is implemented; other set-volume classes return `STATUS_INVALID_PARAMETER`.
