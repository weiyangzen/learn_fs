# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/phys_eject.cpp

## Purpose

`phys_eject.cpp` implements UDFS removable-media eject monitoring and dismount cleanup. It runs in kernel mode and centers on a background waiter thread that polls/receives device events, performs timed metadata/cache flushes, detects media/device loss, and executes the volume dismount/eject sequence.

## Main Entry Points

- `UDFEjectReqWaiter` at line 30: worker routine for eject/media-change monitoring.
- `UDFStopEjectWaiter` at line 673: asks the waiter to stop and optionally waits for completion.
- `UDFDoDismountSequence` at line 704: flushes, unlocks, resets, optionally ejects, and marks the VCB for unsafe IOCTL after dismount.

## Behavior

`UDFEjectReqWaiter` receives a `PUDFEjectWaitContext`, extracts the `PVCB`, target device object, and event capability state, then drains the drive event queue using `IOCTL_CDRW_GET_EVENT` when event polling is enabled. Unsupported event IOCTLs disable event use.

The main loop waits one second at a time on `Vcb->EjectWaiter->StopReq`. If stop is requested, it takes `VCBResource`, clears `Vcb->EjectWaiter`, releases the resource, signals `WaiterStopped`, frees the wait context, and exits.

On each pass it also handles background filesystem maintenance:

- Recomputes free space periodically for modified writable volumes via `UDFGetFreeSpace`.
- Updates `Vcb->LowFreeSpace` and forces a directory-tree flush when the low-space threshold is crossed.
- Honors `UDF_VCB_SKIP_EJECT_CHECK`, `SkipCountLimit`, and `SkipEjectCountLimit` to temporarily skip eject and/or flush work.
- Avoids eject checks while `UDF_VCB_FLAGS_VOLUME_LOCKED` is set.
- Verifies media/write state with `UDFVVerify`.

The timed flush section is skipped for raw disks and for zero flush periods. For non-CDR mode, it increments `BM_FlushTime` and `Tree_FlushTime`, then:

- Flushes the directory tree with `UDFFlushADirectory`, either full or lite depending on bitmap flush timing.
- Flushes cached allocation state for file entries and directories.
- Updates volume identifiers and both main/reserve VDS copies with `UDFUpdateVolIdent` and `UDFUpdateVDS`.
- Updates the logical volume integrity descriptor when appropriate.
- Copies the free-space bitmap to `FSBM_OldBitmap` after changes.
- Calls `WCacheFlushAll__` and clears modified state through `UDFClrModified` when all relevant state was flushed.

The removable-media path first tests device readiness with `IOCTL_CDRW_TEST_UNIT_READY`. Device loss jumps to the common dismount path; media loss disables actual eject and marks `MediaLoss`. Event handling supports both media event class and external request class:

- Media events detect absent/open media and repair buggy `GET_EVENT` present/door-open reports by confirming with `TEST_UNIT_READY`.
- Media eject-request events set `WC->SoftEjectReq`.
- External request key/request events also set `WC->SoftEjectReq`.

Once eject, media loss, or device failure is detected, the waiter sets `Vcb->SoftEjectReq`, disables delayed-close behavior when compiled with `UDF_DELAYED_CLOSE`, closes system delayed files, acquires `VCBResource`, calls `UDFDoDismountSequence`, clears mount/write-security state on media loss, clears waiter fields, signals `WaiterStopped`, frees the wait context, and returns.

`UDFStopEjectWaiter` is the external stop path. It sets the waiter's `StopReq` event under `VCBResource`, then waits on `Vcb->WaiterStopped` when `UDF_VCB_FLAGS_STOP_WAITER_EVENT` is set. It asserts that `Vcb->EjectWaiter` is gone before returning.

`UDFDoDismountSequence` performs the mechanical dismount work:

- Flushes the logical volume with `UDFFlushLogicalVolume`.
- Waits for `BGWriters` to drain.
- Releases write cache state with `WCacheRelease__`.
- Takes `IoResource`.
- Unlocks removable media repeatedly according to `MediaLockCount`.
- Restores read/write drive speed on non-DVD media.
- Resets the lower CDRW driver when this filesystem owns the device-driver path.
- Stops background formatting for MRW media via `IOCTL_CDRW_CLOSE_TRK_SES`.
- Optionally sends `IOCTL_STORAGE_EJECT_MEDIA`.
- Releases `IoResource`.
- Unregisters shutdown notification.
- Clears `UDF_VCB_FLAGS_MEDIA_LOCKED`.
- Sets `UDF_VCB_FLAGS_UNSAFE_IOCTL`.

## Key Dependencies

This file depends heavily on VCB state and synchronization primitives from `udf.h`/included UDFS headers:

- VCB fields: `EjectWaiter`, `VCBResource`, `IoResource`, `VCBFlags`, `Modified`, `LowFreeSpace`, `BM_FlushTime`, `Tree_FlushTime`, `FastCache`, `RootDirFCB`, `TargetDeviceObject`.
- Device IOCTL helpers: `UDFPhSendIOCTL`, `UDFTSendIOCTL`.
- Cache/flush helpers: `UDFFlushADirectory`, `UDFFlushLogicalVolume`, `WCacheFlushAll__`, `WCacheRelease__`.
- Verification/remap helper: `UDFVVerify`.
- Dismount helpers: `UDFCloseAllSystemDelayedInDir`, `UDFCloseAllDelayed`, `UDFResetDeviceDriver`.

## Concurrency and Safety Notes

The file uses `_SEH2_TRY/_SEH2_FINALLY` to guarantee `VCBResource` release when the loop exits early through `try_return`. `IoResource` protects device control sequences. The stop path and waiter cleanup coordinate through kernel events and `Vcb->EjectWaiter`.

The dismount path intentionally sets `UDF_VCB_FLAGS_UNSAFE_IOCTL` after releasing media and driver state. This flag is later used as a guard that the mounted volume should no longer trust ordinary lower-device operations.
