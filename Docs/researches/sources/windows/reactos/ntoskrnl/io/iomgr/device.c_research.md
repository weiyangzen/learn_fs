# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/device.c

This file implements ReactOS I/O manager device-object management: creating, deleting, attaching, detaching, enumerating, and resolving device objects, plus shutdown notification lists and legacy StartIo queue handling.

Key behavior:
- `IoCreateDevice` builds a `DEVICE_OBJECT` plus caller extension and `EXTENDED_DEVOBJ_EXTENSION`, assigns default security, initializes power-manager state, creates VPBs for disk/tape/CD-like devices, initializes device queues, inserts the object, references the owning driver, and links it into `DriverObject->DeviceObject`.
- `IoDeleteDevice`, `IopDereferenceDeviceObject`, and `IopUnloadDevice` coordinate delete-pending state, shutdown deregistration, timer removal, security descriptor release, device-list unlinking, driver unload callbacks, and temporary object conversion.
- `IopAttachDeviceToDeviceStackSafe` attaches a source device above the current top of a target stack under `LockQueueIoDatabaseLock`, rejecting targets that are initializing, unloading, deleting, or being removed. Public attach APIs delegate to it.
- Stack queries include `IoGetAttachedDevice`, `IoGetAttachedDeviceReference`, `IoGetDeviceAttachmentBaseRef`, `IoGetLowerDeviceObject`, `IoGetRelatedDeviceObject`, `IoGetBaseFileSystemDeviceObject`, and target-device relation lookup through a synchronous PnP query.
- Shutdown support keeps first-chance and last-chance shutdown notification lists and sends `IRP_MJ_SHUTDOWN` in `IoShutdownSystem`; phase 1 also shuts down disk, CD-ROM, and tape filesystem queues.
- StartIo support manages keyed and non-keyed device queues, cancel routines, `CurrentIrp`, and deferred StartIo serialization through `StartIoCount`, `StartIoFlags`, and `StartIoKey`.
- Default device security uses predefined public/system DACLs, with special handling for filesystem devices, storage devices, floppy characteristics, admins, and CD-ROM world-read access.

Integration points:
- Depends on object manager APIs (`ObCreateObject`, `ObInsertObject`, references, temporary objects), power manager (`PoInitializeDeviceObject`, `PoVolumeDevice`, `PoRemoveVolumeDevice`), VPB helpers, PnP device-node helpers, and global I/O database locking.
- Driver initialization in `driver.c` calls `IopReadyDeviceObjects` to clear `DO_DEVICE_INITIALIZING` after `DriverEntry`.
- Filesystem shutdown queues are external globals handled by base filesystem shutdown code.

Research notes:
- `IoEnumerateDeviceObjectList` assumes `DriverObject->DeviceObject` is non-NULL; the initial count and first dereference would be unsafe for a driver with no devices.
- `IopDereferenceDeviceObject` accepts `ForceUnload` but asserts it is false, so forced unload is not implemented through that parameter.
- Attach and stack verification take the I/O database lock; `IoDetachDevice` directly modifies attachment fields in this file, so callers must provide any required synchronization.
- Shutdown notification registration uses a single `DO_SHUTDOWN_REGISTERED` flag even though entries can be first-chance or last-chance and removal scans both lists.
