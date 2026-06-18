# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/operations.c

## Purpose

`operations.c` implements the MetadataManager minifilter’s I/O callbacks.

The callbacks demonstrate how a minifilter that keeps an on-volume metadata file open can cooperate with:

- Implicit volume locks from volume opens.
- Explicit `FSCTL_LOCK_VOLUME`, `FSCTL_DISMOUNT_VOLUME`, and `FSCTL_UNLOCK_VOLUME`.
- Volume cleanup/unlock.
- Volume snapshot flush-and-hold-writes.
- Shutdown.
- PnP query remove, cancel remove, and surprise removal.

The recurring pattern is: release metadata references before operations that need exclusive volume access, then reacquire them if the operation fails or the volume becomes usable again.

## `FmmPreCreate`

Handles create/open before the filesystem sees it.

Behavior:

- Defaults to pass-through without post callback.
- Asserts volume-open detection assumptions.
- If target is a volume open:
  - Calls `FmmIsImplicitVolumeLock`.
  - If the create implies a volume lock, calls `FmmReleaseMetadataFileReferences`.
  - On success, requests a post-create callback to determine whether the lock succeeded.
  - On failure, completes the create with the failure status.
- If `VERIFY_METADATA_OPENED` is enabled, requests a post-create callback for non-volume opens.

This is mainly for implicit locks, such as those used by auto-check tools.

## `FmmPostCreate`

Handles post-create completion.

For implicit volume locks:

- If the create/lock failed:
  - Calls `FmmReacquireMetadataFileReferences`.
  - Allows expected failures such as insufficient resources or transition conflict.
- If the create/lock succeeded:
  - Calls `FmmSetMetadataOpenTriggerFileObject` so later cleanup can identify the unlock path.

With verification enabled, successful non-volume creates validate that metadata is open.

The post callback does not fail the already-completed operation.

## `FmmPreCleanup` and `FmmPostCleanup`

`FmmPreCleanup` always returns `FLT_PREOP_SYNCHRONIZE`, forcing a same-thread, low-IRQL post-cleanup callback.

`FmmPostCleanup`:

- Checks volume opens.
- If cleanup succeeded, calls `FmmReacquireMetadataFileReferences`.
- Handles expected failures for dismounted/remounted volumes, invalid device objects, no media, insufficient resources, transition conflicts, and invalid files.

This handles the implicit unlock case where the successful volume-locking handle is cleaned up.

## `FmmPreFSControl`

Handles filesystem-control requests before the filesystem.

Interested FSCTLs:

- `FSCTL_DISMOUNT_VOLUME`
- `FSCTL_LOCK_VOLUME`
- `FSCTL_UNLOCK_VOLUME`

Behavior:

- Ignores non-`IRP_MN_USER_FS_REQUEST` minor functions.
- For lock/dismount on volume opens:
  - Releases metadata references.
  - Requests synchronized post callback if release succeeds.
  - Completes with failure if release fails.
- For unlock:
  - Requests synchronized post callback so metadata can be reacquired after the unlock.

## `FmmPostFSControl`

Handles the result of lock, dismount, and unlock.

### `FSCTL_DISMOUNT_VOLUME`

- On successful dismount:
  - Calls `FltDetachVolume` because the instance is no longer valid.
- On failed dismount:
  - Reacquires metadata references.

### `FSCTL_LOCK_VOLUME`

- On failed lock:
  - Reacquires metadata references.
- On successful lock:
  - Records the target file object as the metadata-open trigger.

### `FSCTL_UNLOCK_VOLUME`

- On successful unlock:
  - Reacquires metadata references.

Expected reacquire failures are treated as sample-tolerated states, generally because the volume may have dismounted/remounted or the instance may be in transition.

## `FmmPreDeviceControl`

Interested IOCTL:

- `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES`

Behavior:

- Gets the instance context.
- Comments explain where a real filter should flush pending metadata and block metadata updates while the snapshot is taking place.
- Passes the instance context as the completion context.
- Requests a post callback.

This sample does not implement real metadata flushing because the metadata contents are not modeled; it shows where that logic belongs.

## `FmmPostDeviceControl`

Handles `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES`.

Behavior:

- Retrieves the instance context from `CbdContext`.
- Comments explain where a real filter should unmark the context and allow metadata updates again.
- Releases the context reference.
- Runs even when draining, so the pre-op context reference is not leaked.

This callback is marked nonpaged in the pragma section.

## `FmmPreShutdown`

On shutdown:

- Calls `FltDetachVolume`.
- Logs failure but does not fail shutdown.
- Returns no post callback.

The sample detaches because the instance is no longer meaningful during shutdown.

## `FmmPrePnp`

Handles selected PnP minor functions.

### `IRP_MN_QUERY_REMOVE_DEVICE`

- Releases metadata references.
- Fails query remove if references cannot be released.

### `IRP_MN_CANCEL_REMOVE_DEVICE`

- Requests synchronized post callback so metadata can be reacquired after the filesystem resumes I/O.

### `IRP_MN_SURPRISE_REMOVAL`

- Detaches the volume instance.

Other PnP minor functions pass through.

## `FmmPostPnp`

Handles `IRP_MN_CANCEL_REMOVE_DEVICE`.

Behavior:

- Asserts the minor function and success status.
- If draining, does nothing.
- Otherwise reacquires metadata references.
- Tolerates insufficient resources and transition conflicts as expected sample cases.

## Callback Registration Implications

The callback behavior assumes the registration in `MetadataManagerInit.c`:

- Create callbacks are optimized to DASD-only unless verification is enabled.
- Cleanup and FSCTL callbacks are synchronized for DASD operations.
- Device control is not restricted to DASD because snapshot IOCTLs are device-level.
- PnP and shutdown callbacks are broad enough to detach or release metadata when volume state changes.

## Research Notes

This file is the operational state machine for metadata ownership:

1. Metadata is normally open while the filter is attached.
2. Before exclusive volume operations, metadata references are dropped.
3. If the exclusive operation fails, metadata is reopened.
4. If the exclusive operation succeeds, the triggering file object is remembered.
5. Cleanup/unlock/cancel remove uses that trigger to reopen metadata.
6. Dismount, shutdown, and surprise removal detach the instance instead.

The code is intentionally conservative: post-operation failures are logged/asserted but do not attempt to rewrite already-completed filesystem results.
