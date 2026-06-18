# File Research: sources/windows/winfsp/src/sys/driver.c

Purpose:
Defines WinFsp kernel driver initialization, device registration, silo-aware global device setup/finalization, privileged unload handling, and global dispatch/callback tables.

Major entry points and roles:
- `DriverEntry` initializes tracing and side-by-side identity, installs all major IRP dispatch routines, installs I/O prepare/complete callback tables, configures Fast I/O and cache-manager callbacks, initializes silos, process buffers, timers, and global control devices.
- `DriverUnload` reverses normal initialization by finalizing devices, timers, process buffers, silos, and tracing.
- `FspDriverMultiVersionInitialize` enables NX pool runtime behavior and detects OS-version-specific features or routines such as `CcCoherencyFlushAndPurgeCache`, `MdlMappingNoWrite`, and a Windows 10 RS4 reparse-point case-sensitivity fix.
- `FspDriverInitializeDevices` creates disk and network filesystem control devices, optionally creates side-by-side symbolic links, creates the internal MUP device, registers an UNC provider with `FsRtlRegisterUncProviderEx`, registers the disk device as a filesystem, and references primary device objects so explicit unload can delete them later.
- `FspDriverFinalizeDevicesEx` unregisters the disk filesystem, deregisters MUP, removes symlinks, and either fully deletes devices or calls `FspDeviceDoIoDeleteDevice` for unload-time teardown.
- `FspDriverUnload` handles the WinFsp control unload request, requiring host silo context and `SE_LOAD_DRIVER_PRIVILEGE`, calling `ZwUnloadDriver`, finalizing every silo's devices, stopping fsvol I/O queues, and deleting remaining device objects.

Dispatch table setup:
- Driver major functions are wired for create, close, read, write, information, EA, volume information, directory control, filesystem/device control, shutdown, lock, cleanup, and security operations.
- Prepare/complete callbacks map asynchronous user-mode transaction paths back to per-operation handlers, including `FspFsvolDirectoryControlPrepare/Complete` and EA completion routines.
- Fast I/O callbacks include read/write, basic/standard/network-open info, query open, device control, section acquisition, modified-write acquisition, and cache flush acquisition. Cache manager callbacks cover lazy write and read-ahead acquisition/release.

Device topology:
- Disk control device name is based on `FSP_FSCTL_DISK_DEVICE_NAME` plus optional side-by-side suffix and uses `FILE_DEVICE_DISK_FILE_SYSTEM`.
- Network control device uses `FSP_FSCTL_NET_DEVICE_NAME` and `FILE_DEVICE_NETWORK_FILE_SYSTEM`.
- The internal MUP device name includes the container GUID when running in a non-host silo, allowing per-container UNC provider identity.
- Only the disk device is registered with `IoRegisterFileSystem`; the network path is handled through MUP registration.

Failure handling:
- `DriverEntry` tracks partial initialization with booleans and unwinds in reverse order on failure.
- `FspDriverInitializeDevices` similarly unwinds registration, MUP, devices, and symbolic links on failure.
- `FspDriverUnload` is serialized by `FspDriverUnloadMutex` and guarded by `FspDriverUnloadDone`.

Dependencies:
- Consumes declarations, global types, and macros from `sys/driver.h`.
- Uses Windows driver APIs: `IoRegisterFileSystem`, `IoUnregisterFileSystem`, `IoCreateSymbolicLink`, `IoDeleteSymbolicLink`, `FsRtlRegisterUncProviderEx`, `FsRtlDeregisterUncProvider`, `ZwUnloadDriver`, `SeSinglePrivilegeCheck`, object references, and fast I/O dispatch structures.
- Depends on WinFsp device, silo, process-buffer, timer, MUP, and I/O queue subsystems implemented in neighboring driver modules.

Research notes:
- This file is the kernel driver's composition root: it does not implement individual filesystem semantics, but it wires every operation into the common dispatch and transaction framework.
- Silo handling is central. Device creation/finalization is called both at global driver startup and per-silo lifecycle.
- Explicit unload is more involved than normal unload because it asks the service manager to unload the driver, finalizes silo devices, stops fsvol I/O queues, and deletes device lists.
