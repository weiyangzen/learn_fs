# File Research: sources/windows/reactos/drivers/filesystems/udfs/udfinit.cpp

This file implements UDF driver initialization, dispatch table setup, filesystem device-object creation, optional forced dismount support, and filesystem registration-change handling.

Key functions:
- `DriverEntry`
  - Zeroes and initializes `UDFGlobalData`.
  - Initializes global and delayed-close resources.
  - Saves the driver object and registry path.
  - Initializes mounted VCB list, internal allocator, delayed-close queues/work item, zones/lookaside structures, and function pointers.
  - Creates the main UDF driver device object and Win32 symbolic link.
  - Creates and registers CD-ROM and, when `UDF_HDD_SUPPORT` is enabled, disk filesystem device objects.
  - Registers `UDFFsNotification` with `IoRegisterFsRegistrationChange`.
  - On failure, unwinds device objects, deadlock detector state, allocator state, zones, and resources.
- `UDFInitializeFunctionPointers`
  - Installs IRP major dispatch handlers for create, close, read, write, file info, volume info, directory control, FS control, device control, shutdown, locks, cleanup, EA, and optional security operations.
  - Initializes the fast I/O dispatch table with check/read/write/query/lock/unlock/section/mod-write/Cc-flush callbacks.
  - Installs cache manager callbacks for lazy write and read-ahead.
  - Sets `DriverObject->DriverUnload = UDFDriverUnload`.
- `UDFCreateFsDeviceObject`
  - Creates a filesystem device object with `UDFFS_DEV_EXTENSION`, zeroes it, and stamps node type/size.
- `UDFDismountDevice`
  - Opens a named device, queries filesystem attributes, skips if already a UDF title, otherwise locks, dismounts, sends CDRW media-change notification, unlocks, closes, and reopens.
- `UDFFsNotification`
  - When another CD-ROM filesystem registers, re-registers UDF’s filesystem device objects under the global resource so UDF can become top-level. It guards against recursive notification using `FsNotification_ThreadId`.

Notable design points:
- The driver registers separate filesystem device objects for CD and HDD-style UDF media.
- Initialization uses nested SEH and manual cleanup rather than RAII.
- Several legacy code paths are disabled with comments or `#if 0`, including broad remount scanning and dynamic NT export lookup.
- Fast I/O uses `FsRtlCopyRead` for read and `UDFFastIoCopyWrite` for write, while cache callbacks are UDF-specific.
