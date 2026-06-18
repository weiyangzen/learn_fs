# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iomgr.c

## Purpose

Initializes the ReactOS I/O manager and defines global I/O manager state, object types, lookaside lists, root object directories, boot partition marking, and top-level I/O subsystem startup sequencing.

## Main Responsibilities

- Defines global I/O manager objects and counters: file/device object types, operation and transfer counters, statistics lock, triage dump storage, and file generic mapping.
- Initializes IRP, MDL, and I/O completion packet lookaside lists globally and per processor.
- Creates object manager types for Adapter, Controller, Device, Driver, IoCompletion, and File objects.
- Creates permanent object directories `\Driver`, `\FileSystem`, and `\FileSystem\Filters`.
- Marks the boot partition device object and stores the boot device for error logging.
- Implements `IoInitSystem`, the high-level boot-time I/O manager initialization sequence.
- Contains an unimplemented `IoInitializeCrashDump` stub.

## Key Functions

- `IopInitLookasideLists` calculates large IRP, small IRP, and MDL sizes; initializes system lookaside lists; configures per-CPU lookaside pointers and IRP float credit.
- `IopCreateObjectTypes` wires object type behavior, including parse/delete/security/query-name callbacks for device, driver, file, and completion objects.
- `IopCreateRootDirectories` creates permanent I/O namespace directories.
- `IopMarkBootPartition` opens the ARC boot device, marks its device object with `DO_SYSTEM_BOOT_PARTITION`, and stores it in `IopErrorLogObject`.
- `IoInitSystem` initializes resources, lists, spin locks, PnP notifications, reserve IRP support, I/O timers, object types, directories, PnP services, WMI, HAL PnP, boot/system drivers, ramdisk boot handling, ARC names, system root, drive letters, and system DLL location.

## Filesystem Relevance

This is the bootstrapping layer that makes the file object type, device object type, filesystem directories, I/O timers, reserve IRPs, and boot volume infrastructure available. Filesystem drivers depend on this setup before they can be loaded, named, attached, and called.

## Dependencies and Coupling

Couples the I/O manager to object manager, executive resources, PnP manager, WMI, HAL, boot loader metadata, ARC name creation, driver loading, ramdisk startup, drive-letter assignment, and process manager system DLL loading.

## Research Notes

- Initialization order is important: object types and directories are created before later driver and filesystem activity.
- Reserve IRP initialization is part of system startup and is later used by paging paths such as `IoPageRead`.
- `IoInitializeCrashDump` is not implemented.
