# File Research: sources/windows/reactos/drivers/filesystems/udfs/devcntrl.cpp

## Purpose

`devcntrl.cpp` implements the UDFS `IRP_MJ_DEVICE_CONTROL` dispatch path. It accepts private UDF IOCTLs, selected storage/CD/DVD/CDRW IOCTLs, volume-control requests, and file allocation-mode requests, and forwards unsupported/default requests to the lower storage device.

## Main Entry Points

- `UDFDeviceControl(PDEVICE_OBJECT, PIRP)`: top-level device-control dispatch wrapper. It enters filesystem context, allocates an IRP context, calls `UDFCommonDeviceControl`, and routes exceptions through the standard UDF exception handler.
- `UDFCommonDeviceControl(PtrUDFIrpContext, PIRP)`: central IOCTL dispatcher. It validates the target object, classifies IOCTL safety, handles local IOCTLs, forwards default IOCTLs to `Vcb->TargetDeviceObject`, and completes or passes through the IRP.
- `UDFDevIoctlCompletion(PDEVICE_OBJECT, PIRP, VOID*)`: completion routine retained for an older forwarding path. It marks pending IRPs and releases the IRP context.
- `UDFGetFileAllocModeFromICB(PtrUDFIrpContext, PIRP)`: returns the file's current ICB allocation mode.
- `UDFSetFileAllocModeFromICB(PtrUDFIrpContext, PIRP)`: flushes the file and converts away from in-ICB allocation mode when allowed.

## IOCTL Target Validation

The dispatcher distinguishes filesystem device object requests from volume/file requests:

- Filesystem device object requests are limited to private control operations such as disabling the driver, invalidating volumes, registering a mount notification event, sending a license key in write builds, and registering autoformat.
- Volume opens accept broad IOCTL handling because the FCB node is the VCB.
- Regular file/directory opens are limited to retrieval pointers and file allocation mode IOCTLs.

The code derives `Fcb`, `Ccb`, and `Vcb` from the file object when possible. Most VCB operations acquire `Vcb->VCBResource` shared; `IOCTL_CDROM_DISK_TYPE` uses exclusive acquisition because it verifies volume/media state.

## Safe Versus Unsafe IOCTLs

`UnsafeIoctl` defaults to true and is cleared for read-only, query, geometry, verify, media-type, audio, CDRW query, UDF query, and dirty-status operations. Before forwarding an unsafe IOCTL, the driver flushes the logical volume with `UDFFlushLogicalVolume`; after handling/defaulting it marks `UDF_VCB_FLAGS_UNSAFE_IOCTL`.

Direct SCSI pass-through is inspected at the CDB level. Write, format, blank, close-track/session, reserve-track, cue-sheet, DVD-structure send, streaming, and write-parameter mode-select commands are treated as direct media modification. If the volume is mounted, the driver closes delayed/system handles, runs `UDFDoDismountSequence`, clears mounted/write-security state, stops the eject waiter, decrements the serial number to defeat quick remount, and then forwards the IOCTL.

## Locally Handled IOCTLs

Important local cases include:

- `IOCTL_UDF_REGISTER_AUTOFORMAT`: stores a single file-object owner in `UDFGlobalData.AutoFormatCount` or returns sharing violation.
- `IOCTL_UDF_DISABLE_DRIVER`: unregisters and deletes the UDF filesystem device object, destroys zones, and tears down global resources.
- `IOCTL_UDF_INVALIDATE_VOLUMES`: releases VCB resource if held and delegates to `UDFInvalidateVolumes`.
- `IOCTL_UDF_SET_NOTIFICATION_EVENT`: references or dereferences a user-provided event handle in `UDFGlobalData.MountEvent`.
- `IOCTL_UDF_IS_VOLUME_JUST_MOUNTED`: returns and clears `Vcb->IsVolumeJustMounted`.
- `IOCTL_UDF_GET_RETRIEVAL_POINTERS` and `IOCTL_UDF_GET_SPEC_RETRIEVAL_POINTERS`: delegate to `UDFGetRetrievalPointers`.
- `IOCTL_UDF_GET_FILE_ALLOCATION_MODE`: delegates to `UDFGetFileAllocModeFromICB`.
- `IOCTL_UDF_SET_FILE_ALLOCATION_MODE`: delegates to `UDFSetFileAllocModeFromICB` in write builds.
- `IOCTL_UDF_LOCK_VOLUME_BY_PID` and `IOCTL_UDF_UNLOCK_VOLUME_BY_PID`: delegate to lock/unlock helpers with the current PID.
- `IOCTL_UDF_GET_VERSION`: fills `UDF_GET_VERSION_OUT` with driver build fields, UDF revision, user FS flags, readonly/raw/media/driver flags, compatibility flags, and config version.
- `IOCTL_UDF_SET_OPTIONS`: accepts temporary config bytes, updates registry-derived VCB options, increments config version, and toggles verify-on-write infrastructure.
- `FSCTL_ALLOW_EXTENDED_DASD_IO`: no-op success.
- `FSCTL_IS_VOLUME_DIRTY`: delegates to `UDFIsVolumeDirty`.
- Eject/media-removal/door-lock controls: either notify an eject waiter, maintain `MediaLockCount`, or forward while normalizing local lock state.
- `IOCTL_CDROM_DISK_TYPE`: verifies media, checks output size, reports data track, and sets audio-track bit if track metadata indicates audio.

## Forwarding Behavior

Default handling calls `IoSkipCurrentIrpStackLocation` and `IoCallDriver(Vcb->TargetDeviceObject, Irp)`. When the IRP is forwarded without local completion, the IRP context is released immediately because no completion routine is currently installed. Local completions set `Irp->IoStatus.Status`, leave or set `Information`, complete the IRP, and release the context in the `finally` block.

## File Allocation Mode Helpers

`UDFGetFileAllocModeFromICB` validates the output buffer, returns `UDFGetFileICBAllocMode__(Fcb->FileInfo)`, and sets `IoStatus.Information`.

`UDFSetFileAllocModeFromICB` validates the input buffer, flushes the file via `UDFFlushAFile`, and refuses conversion to `ICB_FLAG_AD_IN_ICB`. If the current mode is in-ICB and the requested mode is another allocation mode, it calls `UDFConvertFEToNonInICB`; otherwise it permits only no-op mode matches. A notable defect is visible: the function computes `RC` but returns `STATUS_SUCCESS` unconditionally at the end.

## Integration Points

This file is connected to storage/media management code in `fscntrl.cpp`, `verfysup.cpp`, `phys_eject.cpp`, and `Include/phys_lib.cpp` through shared IOCTL helpers and VCB state. It also interacts with user-visible UDF private structures such as `UDF_GET_VERSION_OUT`, `UDF_SET_OPTIONS_IN`, `UDF_GET_FILE_ALLOCATION_MODE_OUT`, and `UDF_SET_FILE_ALLOCATION_MODE_IN`.

## Notable Risks and Edge Cases

- Pass-through CDB inspection assumes the system buffer and CDB data offsets are valid for the expected SCSI structures.
- Unsafe IOCTLs can cause dismount-like local state changes before being forwarded to lower drivers.
- `IOCTL_UDF_DISABLE_DRIVER` tears down global driver state from an IOCTL path; concurrency assumptions are important.
- Event-handle registration allows only one global mount event and relies on user-mode handle referencing/dereferencing correctness.
- The unconditional success return in `UDFSetFileAllocModeFromICB` can hide conversion or flush errors from callers.
- Some private IOCTLs are accepted on the filesystem device object while others require mounted volume context; misuse returns `STATUS_INVALID_PARAMETER`.

## Testing Signals

Useful tests include FS-device IOCTL filtering, file-handle IOCTL rejection, volume-handle version/options queries, safe versus unsafe forwarding, pass-through write CDB media invalidation, eject waiter behavior, media-lock count transitions, output-buffer length validation, and allocation-mode conversion error propagation.
