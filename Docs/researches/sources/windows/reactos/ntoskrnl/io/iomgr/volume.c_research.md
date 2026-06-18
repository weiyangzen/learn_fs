# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/volume.c

## Role

`volume.c` implements volume and filesystem I/O support: VPB creation/reference/freeing, filesystem registration queues, mount probing, verify-volume handling, shutdown dispatch to filesystem drivers, filesystem notification registration, system-partition registry storage, VPB spin-lock wrappers, and conversion from a volume device object to a DOS path via MountMgr.

## Globals and queues

- `IopDatabaseResource` guards filesystem registration and notification queues.
- Queue heads track disk, network, CD-ROM, tape filesystems, and filesystem-change notification entries (lines 18-24).
- `IopFsRegistrationOps` increments on filesystem register/unregister and lets the mount loop detect list mutation while locks were dropped (lines 24, 614-664).

## VPB and device reference helpers

- `IopDecrementDeviceObjectRef()` decrements a device object's reference count under `LockQueueIoDatabaseLock` and calls `IopUnloadDevice()` when the count reaches zero and unload/delete/remove conditions apply (lines 28-58).
- `IopDecrementDeviceObjectHandleCount()` is a wrapper that does not force unload (lines 60-69).
- `IopCreateVpb()` allocates and initializes a nonpaged VPB, linking it to the real device (lines 153-179).
- `IopDereferenceVpbAndFree()` decrements a VPB reference and frees it if unreferenced, still attached to the real device, and not persistent (lines 181-209).
- `IopReferenceVerifyVpb()` references a mounted VPB and returns its filesystem device object for verify operations (lines 214-245).
- `IopMountInitializeVpb()` marks a VPB mounted, optionally raw, adjusts the mounted filesystem device stack size, stores the VPB in the device extension, and references it (lines 247-278).
- `IoAcquireVpbSpinLock()` and `IoReleaseVpbSpinLock()` wrap `LockQueueIoVpbLock` (lines 1199-1219).

## Mount and verify flow

- `IopCheckVpbMounted()` loops until a device VPB is mounted. It computes whether raw mount is allowed from an empty remaining name with no related file object, calls `IopMountVolume()`, handles alert/user APC interruption as `STATUS_WRONG_VOLUME`, and references an already mounted VPB unless locked (lines 71-151).
- `IopMountVolume()` serializes on the device lock unless already locked, acquires `IopDatabaseResource`, skips mounted/remove-pending devices, chooses the filesystem queue from the real device type, and iterates registered filesystems until one accepts `IRP_MN_MOUNT_VOLUME` (lines 460-778).
- During mount probing, it finds the top attached target device, allocates an IRP with storage-stack plus filesystem-stack overhead, sets `IRP_MJ_FILE_SYSTEM_CONTROL/IRP_MN_MOUNT_VOLUME`, passes the VPB and target device, drops the database lock while calling the filesystem, and reacquires it after completion (lines 503-636).
- Mount success calls `IopMountInitializeVpb()`. Failures handle user-induced errors, concurrent registration changes, `STATUS_FS_DRIVER_REQUIRED` by calling `IopLoadFileSystemDriver()` and restarting, raw-mount restrictions, and total device failures (lines 637-743).
- On boot partition mount failure before initialization phase 2, `IopMountVolume()` bugchecks with `INACCESSIBLE_BOOT_DEVICE` (lines 763-774).
- `IoVerifyVolume()` locks the device, sends `IRP_MN_VERIFY_VOLUME` to the current filesystem stack when mounted, dereferences the VPB, and if it gets `STATUS_WRONG_VOLUME` creates a new VPB and tries to mount again with raw-mount allowance from the caller (lines 872-980).

## Filesystem registration and notification

- `IoRegisterFileSystem()` selects the queue by filesystem device type, inserts high-priority filesystems at the head and low-priority ones near the tail, increments registration operations, clears `DO_DEVICE_INITIALIZING`, notifies registered listeners, releases the resource, and increments the device reference count to prevent unload (lines 982-1049).
- `IoUnregisterFileSystem()` removes a queued filesystem, notifies listeners inactive, increments registration operations, and decrements the unload-prevention reference (lines 1051-1082).
- `IopNotifyFileSystemChange()` walks `IopFsNotifyChangeQueueHead` and calls each registered notification procedure (lines 280-306).
- `IoRegisterFsRegistrationChange()` rejects an immediately repeated registration from the same driver/routine pair, allocates a notification entry, inserts it, notifies the caller about already registered network/CD/disk/tape filesystems, references the driver object, and returns success (lines 1084-1150).
- `IoUnregisterFsRegistrationChange()` removes the matching notification entry and dereferences the driver object (lines 1152-1197).
- `IoEnumerateRegisteredFiltersList()` returns the registered notification driver objects, referencing each object copied into the caller buffer and reporting `STATUS_BUFFER_TOO_SMALL` if the supplied array is insufficient (lines 819-870).

## Shutdown and filesystem loading

- `IopShutdownBaseFileSystems()` walks a filesystem queue, references each top attached device, builds an `IRP_MJ_SHUTDOWN`, calls the driver, waits if pending, clears the event, and releases references (lines 344-402).
- `IopLoadFileSystemDriver()` sends an `IRP_MN_LOAD_FILE_SYSTEM` filesystem-control IRP to the top attached device for an FsRec-like recognizer. A reference decrement call is commented out because it broke second-stage boot (lines 407-455).

## Other public APIs

- `IoSetSystemPartition()` stores a `REG_SZ` `SystemPartition` value under `HKLM\SYSTEM\Setup` using the provided volume-name string (lines 1221-1272).
- `IoVolumeDeviceToDosName()` queries the volume device for its mountdev name, opens MountMgr, queries `IOCTL_MOUNTMGR_QUERY_DOS_VOLUME_PATH` first for size and then for data, allocates a caller-owned buffer, moves the first multi-string DOS path into the returned `UNICODE_STRING`, and dereferences the MountMgr file object (lines 1274-1430).

## Implementation gaps and risks

- `IopDecrementDeviceObjectRef()` is marked half-implemented (lines 28-30).
- `IopLoadFileSystemDriver()` builds a device-control IRP using `IRP_MJ_DEVICE_CONTROL` as the IOCTL code and then overwrites the stack to filesystem-control/load-filesystem. This works with the local builder but is non-obvious and should be treated as a compatibility shim (lines 426-444).
- `IoRegisterFileSystem()` uses `InsertTailList(FsList->Blink, ...)` for low-priority insertion (lines 1021-1031). This is unusual because `InsertTailList()` normally takes the list head; verify list ordering assumptions before changing it.
- Several code paths drop and reacquire `IopDatabaseResource` while preserving a local restart list. Mount behavior is sensitive to registration races and reference-count correctness (lines 614-722).
- `IoRegisterFsRegistrationChange()` duplicate detection only checks the current tail entry rather than the full notification list (lines 1099-1116).
