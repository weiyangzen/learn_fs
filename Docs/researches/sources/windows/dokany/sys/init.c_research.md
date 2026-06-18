# File Research: sources/windows/dokany/sys/init.c

Implements global driver device creation, per-mount disk device creation, mount-entry management, mount-point symbolic links, UNC provider registration, device-delete delay handling, and teardown staging.

Key entry points:
- `DokanCreateGlobalDiskDevice()` creates the global control device, disk/CD filesystem recognizer devices, symbolic link, resources, mount/delete lists, and delayed-delete thread.
- `DokanCreateDiskDevice()` creates a per-mount disk device, names it from a generated GUID, initializes its DCB, IRP/event queues, resources, cache callbacks, mount point, UNC name, symbolic link, and output `DOKAN_CONTROL`.
- `DokanDeleteDeviceObject()` removes mount entries, disables interfaces, deregisters network provider, logs allocation counters, and queues disk/volume devices for delayed deletion.
- `DokanDeleteDeviceThread()` and `DeleteDeviceDelayed()` periodically delete volume/disk device objects once reference counts drain.
- `InsertMountEntry()`, `RemoveMountEntry()`, `FindMountEntry()`, `FindMountEntryByName()`, and `DokanGetMountPointList()` manage the global mount table.
- `InsertDeviceToDelete()`, `InsertDcbToDelete()`, and `FindDeviceForDeleteBySessionId()` manage delayed deletion records and session cleanup.
- `IsMounted()`, `IsDeletePending()`, `IsUnmountPending()`, and `IsUnmountPendingVcb()` centralize lifecycle state checks.
- `DokanCreateMountPoint()`, `DokanDeleteMountPoint()`, `DeleteMountPointSymbolicLink()`, and system-thread helper routines create/delete drive-letter or directory mount links.
- `DokanRegisterUncProvider()` and `DokanDeregisterUncProvider()` register network filesystems with MUP.
- `DokanSetVolumeSecurity()` applies an optional DACL to the created volume device.

Core mechanics:
- The global device registers Dokan filesystem devices with `IoRegisterFileSystem()` and marks them for direct I/O and low-priority filesystem ordering.
- Disk device creation distinguishes disk and network filesystems, disables mount manager for network filesystems, and normalizes mount-point strings under `\DosDevices\`.
- DCB initialization creates pending IRP, notify event, and pending retry lists; initializes remove lock, kill/release/force-timeout events, resources, and cache-manager no-op callbacks.
- Mount entries have a global list lock and per-entry resource. Lookup can match by mount point/session or disk device name.
- Non-admin mount list retrieval filters out mount points from other sessions.
- Delayed deletion waits several cycles and requires reference counts to drop before deleting symbolic links and device objects.
- Mount-manager removal differs for drive-letter versus directory mount points: drive letters use volume delete points, directories delete reparse points and notify mount manager.

Important invariants:
- Delayed deletion avoids deleting device objects while outstanding references remain.
- Mount-point list and mount-entry resources must be acquired in consistent order; `RemoveMountEntry()` refetches under list lock for this reason.
- Session-specific mount cleanup keeps deletion entries alive until the session mount-point link has been removed.
- Network UNC provider operations run in a system thread.
- DCB names are freed only after symbolic link/device teardown has reached the delayed-delete stage.

Filesystem relevance:
- This file is Dokan's lifecycle and namespace foundation: it creates Windows-visible devices and mount points, tracks active mounts, and safely tears down volume/disk objects after unmount.

Notable risks:
- `RemoveMountEntry()` returns early without releasing `MountPointListLock` if the entry is already removed; that path is worth auditing.
- Device deletion relies on reference counts and a fixed minimum delay before deleting objects.
- Mount-manager and directory reparse-point paths are sensitive to reentrant mount operations and global automount state.
