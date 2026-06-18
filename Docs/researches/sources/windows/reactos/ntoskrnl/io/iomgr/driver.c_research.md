# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/driver.c

This file implements driver-object lifecycle management, boot/system driver initialization, dynamic driver load/unload, reinitialization callbacks, and driver object extensions.

Key behavior:
- `IopGetDriverNames` derives the kernel driver object name from the service key, using `ObjectName` when present or constructing `\Driver\<ServiceName>` / `\FileSystem\<ServiceName>` from the service `Type`.
- `IopNormalizeImagePath` normalizes empty or relative image paths to `\SystemRoot\System32\drivers\<service>.sys` or `\SystemRoot\<relative>`.
- `IopInitializeDriverModule` creates a permanent driver object for a loaded image, initializes dispatch entries to `IopInvalidDeviceRequest`, copies service/driver names, calls `DriverEntry`, fixes illegal NULL major functions, frees init pages, marks devices ready, and optionally runs reinitialization.
- Boot-driver support resolves imports for loader-provided modules, derives service names from module filenames, opens service keys, initializes built-in boot drivers in group/tag order, processes service `Enum` entries, queues AddDevice work for matching PDOs, and triggers root/device-tree enumeration.
- `IopInitializeSystemDrivers` performs a synchronous device-tree enumeration, loads registry-selected system drivers with `ZwLoadDriver`, and queues another tree enumeration.
- `IopUnloadDriver` enforces `SeLoadDriverPrivilege`, resolves the driver object, validates the service image path, marks devices unload-pending, checks for references or attached devices, calls `DriverUnload` through the system-process worker path, and makes the driver object temporary.
- `IoCreateDriver` creates built-in driver objects with optional generated names, initializes default dispatchers, calls the supplied initialization function, and fixes NULL dispatch entries.
- Reinitialization APIs enqueue boot and normal reinit callbacks; `IopReinitializeDrivers` and `IopReinitializeBootDrivers` drain those queues, increment the driver extension count, clear registration flags, and call the callbacks.
- Driver object extension APIs allocate and find client extensions keyed by caller-provided identification address.
- `NtLoadDriver` and `NtUnloadDriver` are the public system calls; actual load/unload work is marshaled to `PsInitialSystemProcess` when needed by `IopDoLoadUnloadDriver`.

Integration points:
- Uses memory manager image loading/unloading (`MmLoadSystemImage`, `MmUnloadSystemImage`, `MmFreeDriverInitialization`) and import resolution.
- Coordinates closely with PnP globals/actions (`PnpSystemInit`, `PnPBootDriversLoaded`, `PiQueueDeviceAction`, `PiPerformSyncDeviceAction`, `PiEnumerationFinished`).
- Calls `IopReadyDeviceObjects` from `device.c` after successful image-driver initialization.
- Uses registry service configuration for names, type, image path, group order, tag order, and enumerated device instances.

Research notes:
- `IopUnloadDriver` sets `DOE_UNLOAD_PENDING` on each device before proving unload is safe; if references or attached devices prevent unload, it returns success without visibly clearing those flags.
- `IopLoadDriver` calls `IopNormalizeImagePath(&ImagePath, NULL)`; if a registry `ImagePath` value is an empty string, the empty-path branch expects a non-NULL service name.
- `IoAllocateDriverObjectExtension` and `IoGetDriverObjectExtension` raise IRQL to DPC level but do not take a visible interprocessor lock around the linked list, so concurrent extension operations may need external serialization.
- `IoCreateDriver` does not visibly call `IopReadyDeviceObjects` after successful initialization, unlike `IopInitializeDriverModule`.
- Boot initialization includes setup-loader hacks and assumes certain registry/loader invariants; several failure paths return early after partial setup.
