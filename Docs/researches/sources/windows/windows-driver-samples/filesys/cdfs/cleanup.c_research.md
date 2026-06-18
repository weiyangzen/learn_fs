# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cleanup.c

## Purpose

`cleanup.c` implements `CdCommonCleanup`, the CDFS cleanup path invoked when the last user handle for a file object is closed. Cleanup is distinct from close: the file object may still exist due to MM/cache references, but user-visible handle state must be released.

## Main Flow

`CdCommonCleanup`:

1. Completes immediately with success if the request targets the filesystem device object rather than a mounted volume.
2. Decodes the file object into `TypeOfOpen`, FCB, and CCB.
3. Completes immediately for unopened or stream file objects.
4. Acquires the file exclusively long enough to set `FO_CLEANUP_COMPLETE`, preventing future reads through this file object.
5. Handles special volume-open cases:
   - If `CCB_FLAG_DISMOUNT_ON_CLOSE` is set, acquires CdData and forces dismount check.
   - If the volume handle modified the device, flushes the lower device and marks it for verify.
6. Acquires the FCB exclusively and performs type-specific cleanup:
   - `UserDirectoryOpen`: calls `FsRtlNotifyCleanup` for pending directory notifications.
   - `UserFileOpen`: runs oplock cleanup, unlocks all byte-range locks for this file object/process, uninitializes the cache map, and refreshes fast-I/O possibility.
   - `UserVolumeOpen`: no file-specific cleanup.
7. Locks the VCB to decrement FCB/VCB cleanup counts.
8. If this file object locked the volume, clears `VPB_LOCKED`, clears `VCB_STATE_LOCKED`, clears `VolumeLockFileObject`, and later sends `FSRTL_VOLUME_UNLOCK`.
9. Removes share access from the FCB.
10. Releases the FCB and sends unlock notification if needed.
11. If cleanup count reached zero on an unmounted VCB, acquires CdData and VCB exclusively and calls `CdPurgeVolume` to spark teardown.
12. Completes the IRP with `STATUS_SUCCESS`.

## Integration

This routine is called from `CdFsdDispatch`/FSP dispatch for `IRP_MJ_CLEANUP`. It interacts with:

- file-object decoding
- file/FCB/VCB synchronization
- oplock and file-lock packages
- cache manager
- notify package
- volume lock/dismount state
- share access accounting
- volume purge/teardown

## Important Semantics

- Cleanup marks user handle closure, not object deletion.
- Share access is removed during cleanup because close may be delayed by mapped sections.
- Volume unlock notification is sent after releasing locks.
- Teardown is attempted only after counts indicate no outstanding cleanup handles and the VCB is not mounted.

## Risk Notes

- Lock ordering matters: the routine carefully limits early file acquisition, then uses FCB and VCB locks for count/share updates.
- Device flush on modified volume handles uses IRP hijacking, so control flow differs from normal completion.
- Oplock cleanup is expected to complete immediately in this path.
- Failure during the purge attempt is not propagated; the cleanup IRP still completes success after teardown stimulation.
