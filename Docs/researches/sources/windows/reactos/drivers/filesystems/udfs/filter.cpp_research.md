# File Research: sources/windows/reactos/drivers/filesystems/udfs/filter.cpp

`filter.cpp` contains the small filter-attachment support used to attach UDFS above another CD-ROM filesystem device, especially CDFS-style stacks. It creates a filter device object, initializes its extension, and attaches it to the current top of the target filesystem device stack.

Key routines:
- `UDFCheckOtherFS()` acquires `UDFGlobalData.GlobalDataResource`, creates a `FILE_DEVICE_CD_ROM_FILE_SYSTEM` device with `FILTER_DEV_EXTENSION`, tags it as `UDF_NODE_TYPE_FILTER_DEVOBJ`, records the lower filesystem device, and attaches with `IoAttachDeviceByPointer()`.
- `UDFCheckOtherFSByName()` resolves a named device object via `IoGetDeviceObjectPointer()`, calls `UDFCheckOtherFS()`, then dereferences the file object.
- `UDFFsNotification()` is present but compiled out with `#if 0`; it would attach when a CD-ROM filesystem registers as active.

Notable behavior and dependencies:
- The filter path distinguishes filter device extensions by `NodeIdentifier` values used later in mount handling.
- Failed filter-device creation or attachment cleans up immediately and releases the global resource.
- The active filesystem notification path is disabled, so callers must invoke the name/device attachment helpers through other initialization logic.
