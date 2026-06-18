# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/rawfs.c

## Role

`rawfs.c` implements the RAW filesystem driver used when no real filesystem recognizes a volume. It creates raw disk/CD/tape filesystem device objects, mounts a volume device object around an underlying device, provides minimal open/close/cleanup, forwards read/write/device-control IRPs, handles basic lock/dismount FSCTLs, and returns minimal volume information.

## Key structures and globals

- `VCB` tracks the target device, public VPB, temporary local VPB, state flags, open count, share access, mutex, bytes per sector, and sector count (lines 17-30).
- `VOLUME_DEVICE_OBJECT` embeds a `DEVICE_OBJECT` plus the RAW VCB (lines 32-36).
- State flags are `VCB_STATE_LOCKED` and `VCB_STATE_DISMOUNTED` (lines 38-39).
- Global filesystem device objects are `RawDiskDeviceObject`, `RawCdromDeviceObject`, and `RawTapeDeviceObject` (line 43).

## Mount and VPB lifecycle

- `RawInitializeVcb()` zeroes the VCB, stores the target device and VPB, initializes the mutex, and allocates a local VPB used during later dismount transitions (lines 47-76).
- `RawCheckForDismount()` must run with the VCB mutex held. It locks the VPB spin lock, decides whether references allow deletion, may install a local VPB on the real device while marking the current VPB persistent, or clears the mounted state and deletes the RAW volume device when the last reference is gone (lines 78-158).
- `RawMountVolume()` creates a `FILE_DEVICE_DISK_FILE_SYSTEM` volume device, initializes its VCB using the mount VPB, sets dummy serial/label fields, sets stack size/sector size/direct I/O, creates a stream file object for notification, emits `FSRTL_VOLUME_MOUNT`, and drops temporary open-count inflation used to avoid immediate dismount during notification (lines 379-461).

## IRP handling

- `RawDispatch()` distinguishes the filesystem control device object from RAW volume device objects. On the filesystem device object it only succeeds create/cleanup/close stubs unless processing a mount request. On volume device objects it enters filesystem context and dispatches to per-major handlers (lines 1045-1153).
- `RawCreate()` permits only an unnamed non-directory `FILE_OPEN`, rejects locked or dismounted volumes, enforces share access, increments open count, attaches the file object to the VPB, marks `FO_NO_INTERMEDIATE_BUFFERING`, and attempts dismount if the open fails and no opens remain (lines 227-336).
- `RawClose()` ignores stream file objects, otherwise decrements open count under the VCB mutex and may dismount on the final close (lines 187-225).
- `RawCleanup()` removes share access and, if the VCB is dismounted, calls dismount handling while asserting one open remains (lines 1010-1043).
- `RawReadWriteDeviceControl()` immediately succeeds zero-length read/write requests, otherwise copies the stack to the next device, sets `SL_OVERRIDE_VERIFY_VOLUME`, installs `RawCompletionRoutine()`, and forwards to the target device (lines 338-377).
- `RawCompletionRoutine()` updates synchronous file-object byte offsets for successful reads and writes and propagates pending state (lines 160-185).

## FSCTL and information support

- `RawUserFsCtrl()` implements oplock requests as `STATUS_NOT_IMPLEMENTED`, `FSCTL_LOCK_VOLUME`, `FSCTL_UNLOCK_VOLUME`, and `FSCTL_DISMOUNT_VOLUME`, and emits corresponding `FsRtlNotifyVolumeEvent()` notifications (lines 463-573).
- `RawFileSystemControl()` handles user FSCTLs, mount volume, and verify volume. Verify returns `STATUS_WRONG_VOLUME`, clears `DO_VERIFY_VOLUME`, and may dismount (lines 575-639).
- `RawQueryInformation()` and `RawSetInformation()` only support `FilePositionInformation`, including alignment validation on set (lines 641-733).
- `RawQueryFsVolumeInfo()` returns an empty label and the VPB serial number (lines 735-754).
- `RawQueryFsSizeInfo()` queries drive geometry and, for non-floppy devices, partition information to fill `FILE_FS_SIZE_INFORMATION` (lines 756-893).
- `RawQueryFsDeviceInfo()` reports `FILE_DEVICE_DISK` and target characteristics (lines 895-920).
- `RawQueryFsAttributeInfo()` reports filesystem name `RAW` and no attributes (lines 922-948).
- `RawQueryVolumeInformation()` dispatches the supported filesystem information classes and completes the IRP with consumed length (lines 950-1008).

## Driver initialization and teardown

- `RawFsDriverEntry()` creates `\Device\RawDisk`, `\Device\RawCdRom`, and `\Device\RawTape`, marks them direct-I/O, installs the dispatch table, registers shutdown/unload, and registers all three file systems (lines 1190-1279).
- `RawShutdown()` contains disabled unregister/delete logic due to a shutdown freeze comment and currently only completes success (lines 1155-1176).
- `RawUnload()` is effectively disabled because the unload path is not expected to run (lines 1178-1188).

## Implementation gaps and risks

- RAW is intentionally minimal: no directory/file namespace, no allocation accounting beyond whole-device size, no real volume label, and limited information classes.
- `RawQueryFsDeviceInfo()` always reports `FILE_DEVICE_DISK` even when the RAW filesystem instance is for CD-ROM or tape (lines 912-916).
- `RawUserFsCtrl()` returns success for dismount when locked but does not set `VCB_STATE_DISMOUNTED` in that branch, so actual dismount semantics are incomplete (lines 528-542).
- Shutdown unregister/delete is disabled under `#if 0`, leaving lifetime mostly static (lines 1155-1170).
