# File Research: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.c

## Purpose

`ntfs.c` is the NTFS driver entry module. It creates the filesystem device object, initializes global state, registers dispatch and fast-I/O entry points, initializes lookaside lists, reads the experimental write-support registry switch, and registers the filesystem with the I/O manager.

## Main Functions

`DriverEntry`

- Creates the `\Ntfs` device with type `FILE_DEVICE_DISK_FILE_SYSTEM`.
- Stores and initializes `NtfsGlobalData` in the device extension.
- Initializes the global resource.
- Disables write support by default.
- Reads registry value `MyDataDoesNotMatterSoEnableExperimentalWriteSupportForEveryNTFSVolume`; if present and true, enables write support globally.
- Calls `NtfsInitializeFunctionPointers`.
- Installs cache manager callbacks for lazy write and read-ahead.
- Installs fast-I/O callbacks for check, read, and write.
- Initializes nonpaged lookaside lists for IRP contexts, FCBs, and attribute contexts.
- Sets `DriverUnload` to `NULL`.
- Marks the filesystem device as `DO_DIRECT_IO`.
- Calls `IoRegisterFileSystem` and references the device object.

`NtfsInitializeFunctionPointers`

- Routes supported major functions to `NtfsFsdDispatch`:
  - create, close, cleanup
  - read, write
  - query/set file information
  - query/set volume information
  - directory control
  - filesystem control
  - device control

## Integration

This file owns the global `PNTFS_GLOBAL_DATA NtfsGlobalData`. The lookaside lists it initializes are used throughout the driver by `misc.c`, `mft.c`, FCB code, and mount/volume paths. The dispatch table points all handled IRPs into the common dispatch layer declared in `ntfs.h`.

## Notable Behavior

- Write support is deliberately gated behind a long, explicit registry value name and remains off by default.
- The driver cannot be unloaded after initialization.
- Fast I/O is advertised through callbacks, but actual capability depends on the implementations in `fastio.c`.
