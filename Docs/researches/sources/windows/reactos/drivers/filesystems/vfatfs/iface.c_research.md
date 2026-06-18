# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/iface.c

## Purpose

`iface.c` contains `DriverEntry()` for the ReactOS VFAT/FATX filesystem driver. It creates the global filesystem device, initializes `VfatGlobalData`, installs dispatch vectors, cache-manager callbacks, fast I/O support, lookaside lists, close/dismount global state, and registers the filesystem with the I/O manager.

## Main Contents

- Creates the global device named `\FatX` with `FILE_DEVICE_DISK_FILE_SYSTEM`.
- Stores global driver/device pointers, processor count, and optional corruption-break flag.
- Initializes delayed close support:
  - close mutex
  - close list
  - close counter
  - close worker state
  - shutdown-started flag
  - work item allocated against the global device object
- Sets `DO_DIRECT_IO` on the global device.
- Routes nearly all major IRP functions to `VfatBuildRequest`; shutdown uses `VfatShutdown` directly.
- Installs cache-manager callbacks for lazy write and read-ahead.
- Initializes fast I/O through `VfatInitFastIoRoutines()`.
- Creates lookaside lists for FCBs, CCBs, IRP contexts, and delayed-close contexts.
- Initializes the mounted-volume list and registers the filesystem with `IoRegisterFileSystem()`.
- Under `KDBG`, registers `vfatKdbgHandler()`.

## Integration

This file is the entry point for all later files in the VFAT driver. `misc.c` owns the common request builder/dispatcher that most major functions enter through, while `fsctl.c`, `rw.c`, `volume.c`, `pnp.c`, and others implement the actual per-major-function behavior.

## Research Notes

Unload is explicitly disabled (`DriverUnload = NULL`). Failure handling is narrow: if close work-item allocation fails, the global device is deleted and initialization aborts.
