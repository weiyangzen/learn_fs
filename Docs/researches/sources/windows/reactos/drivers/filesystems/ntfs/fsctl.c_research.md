# File Research: sources/windows/reactos/drivers/filesystems/ntfs/fsctl.c

Read status: complete file, 1005 lines.

This file implements filesystem control handling, NTFS volume recognition, mount setup, volume metadata loading, and several user FSCTLs.

Key mount/volume helpers:
- `NtfsHasFileSystem()` queries disk geometry/partition info, reads the boot sector, validates the `"NTFS    "` OEM ID, reserved zero fields, and supported cluster sizes.
- `NtfsQueryMftZoneReservation()` reads the `NtfsMftZoneReservation` registry value.
- `NtfsGetVolumeData()` reads the boot sector into `NtfsInfo`, initializes file-record lookaside storage, reads the MFT record, finds the MFT `$DATA`, reads the `$Volume` record, extracts volume label/version/flags, creates the volume FCB, and stores MFT-zone reservation.
- `NtfsMountVolume()` validates the target, creates the volume device object, initializes the VCB, wires VPB fields, creates the stream file object and cache map, initializes resources/spin locks, sets VPB serial/label, and sends a mount notification.
- `NtfsVerifyVolume()` is a stub returning `STATUS_WRONG_VOLUME`.

Key user FSCTL helpers:
- `GetNfsVolumeData()` fills `NTFS_VOLUME_DATA_BUFFER` and optional extended version data.
- `GetNtfsFileRecord()` returns an in-use file record at or before the requested file reference.
- `GetVolumeBitmap()` validates/probes METHOD_NEITHER buffers, reads `$Bitmap:$DATA`, and returns bitmap bytes starting at an 8-cluster-aligned LCN.
- `LockOrUnlockVolume()` toggles `VCB_VOLUME_LOCKED` only for volume opens and only allows locking when the caller is the only open handle.
- `NtfsUserFsRequest()` dispatches implemented FSCTLs and returns `STATUS_NOT_IMPLEMENTED` for many USN, retrieval, move, and volume resize controls.
- `NtfsFileSystemControl()` dispatches mount, verify, and user filesystem requests by minor function.

Important dependencies:
- Low-level I/O helpers in `blockdev.c`.
- File-record and attribute readers across the NTFS driver.
- Cache manager and VPB/device-object setup.

Notable behavior and risks:
- `GetNtfsFileRecord()` decrements the requested MFT record until it finds an in-use record, with no visible lower bound.
- Several volume-data fields are placeholders: total reserved, MFT zone start, and MFT zone end.
- Many FSCTLs are intentionally unimplemented.
- Failure cleanup in mount/setup paths is partial and depends on which initialization milestones were reached.
