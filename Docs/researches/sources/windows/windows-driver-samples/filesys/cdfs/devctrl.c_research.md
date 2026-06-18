# File Research: sources/windows/windows-driver-samples/filesys/cdfs/devctrl.c

CDFS filesystem device-control dispatch support for volume opens.

Key responsibilities:
- Implements `CdCommonDevControl`.
- Accepts device-control requests only on `UserVolumeOpen` file objects.
- Verifies the VCB for TOC reads and disk-type queries.
- Handles `IOCTL_CDROM_DISK_TYPE` directly from `Vcb->DiskFlags`.
- Passes other accepted IOCTLs through to the target CD-ROM device object.
- Provides `CdDevCtrlCompletionRoutine` to preserve pending state on pass-through completion.

Important behavior:
- Non-volume opens receive `STATUS_INVALID_PARAMETER`.
- `IOCTL_CDROM_DISK_TYPE` requires an output buffer large enough for `CDROM_DISK_DATA`; otherwise it returns `STATUS_BUFFER_TOO_SMALL`.
- Pass-through requests copy the current IRP stack location to the next stack location and call `IoCallDriver`.
- After passing the IRP down, CDFS completes only its IRP context, not the IRP itself.

Dependencies:
- Depends on `CdDecodeFileObject`, `CdVerifyVcb`, `CdCompleteRequest`, and the mounted VCB target device object.
- Uses normal Windows completion-routine pending propagation via `IoMarkIrpPending`.

Notable risks:
- The accepted IOCTL surface is intentionally narrow at the filesystem layer; most semantics are delegated to the lower CD-ROM stack.
- The completion routine returns `STATUS_SUCCESS`, so lower-driver completion continues normally after pending-state fixup.
