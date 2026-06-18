# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatinit.c

## Purpose

`fatinit.c` implements FastFAT driver initialization and unload support. It creates the filesystem device objects, wires the IRP and Fast I/O dispatch tables, initializes global driver state, reads compatibility registry options, registers filter callbacks, and registers FAT as a disk and CD-ROM filesystem with the I/O manager.

## Main Entry Points

- `DriverEntry`
  - Creates `\Fat` as `FILE_DEVICE_DISK_FILE_SYSTEM`.
  - Creates `\FatCdrom` as `FILE_DEVICE_CD_ROM_FILE_SYSTEM`.
  - Assigns every FastFAT `IRP_MJ_*` dispatch routine into `DriverObject->MajorFunction`.
  - Initializes `FatFastIoDispatch` with Fast I/O read/write/query/lock/MDL callbacks.
  - Registers `FatFilterCallbackAcquireForCreateSection` with `FsRtlRegisterFileSystemFilterCallbacks`.
  - Zeroes and initializes global `FatData`.
  - Initializes close queues, work item, zero page, spin lock, resources, lookaside lists, cache manager callbacks, processor count, and global process pointer.
  - Reads registry values controlling Chicago compatibility mode and code-page invariance.
  - Registers both filesystem device objects with `IoRegisterFileSystem`.
  - Detects Fujitsu FMR hardware.
  - On Windows 8+ caches global disk accounting state via `PsIsDiskCountersEnabled`.

- `FatUnload`
  - Deletes nonpaged lookaside lists.
  - Deletes `FatData.Resource`.
  - Frees the close work item.
  - Dereferences the disk and CD-ROM filesystem device objects.
  - Notably does not delete all objects or free every allocation initialized in `DriverEntry`; this mirrors a filesystem driver unload path that depends on broader lifetime assumptions.

- `FatGetCompatibilityModeValue`
  - Opens `\Registry\Machine\System\CurrentControlSet\Control\FileSystem`.
  - Queries a DWORD-like value by name.
  - Uses a fixed stack buffer first, then grows a paged-pool buffer on `STATUS_BUFFER_OVERFLOW`.
  - Returns the registry value through `Value` only on success with nonzero data length.

- `FatIsFujitsuFMR`
  - Opens `\Registry\Machine\Hardware\DESCRIPTION\System`.
  - Reads the `Identifier` value.
  - Returns true when the value begins with `FUJITSU FMR-`.

## Important Constants

- `COMPATIBILITY_MODE_KEY_NAME`: filesystem control registry key.
- `COMPATIBILITY_MODE_VALUE_NAME`: `Win31FileSystem`; inverted into `FatData.ChicagoMode`.
- `CODE_PAGE_INVARIANCE_VALUE_NAME`: `FatDisableCodePageInvariance`; inverted into `FatData.CodePageInvariant`.
- `KEY_WORK_AREA`: initial registry query buffer size.
- `REGISTRY_HARDWARE_DESCRIPTION_W`, `REGISTRY_MACHINE_IDENTIFIER_W`, `FUJITSU_FMR_NAME_W`: hardware detection inputs.

## Initialization Flow

1. Create named filesystem device objects.
2. Set dispatch and Fast I/O tables.
3. Register FS filter callback for section synchronization.
4. Initialize `FatData` and global queues.
5. Allocate close work item and zero page.
6. Tune close/list lookaside depth from `MmQuerySystemSize`.
7. Initialize cache manager callbacks.
8. Read registry behavior toggles.
9. Initialize resources and lookaside lists.
10. Register with the I/O manager.
11. Record hardware/platform features.
12. Return `STATUS_SUCCESS`.

## Error Handling

- Device creation failure returns immediately.
- If CD-ROM filesystem device creation fails, the disk filesystem device is deleted.
- Filter callback registration failure deletes both device objects.
- Work item and zero-page allocation failures return `STATUS_INSUFFICIENT_RESOURCES`.
- Registry lookup failures are tolerated; defaults are used.

## Dependencies

This file depends heavily on declarations from `fatprocs.h`, especially:

- Global variables: `FatData`, `FatDiskFileSystemDeviceObject`, `FatCdromFileSystemDeviceObject`, `FatFastIoDispatch`, lookaside lists, close queues.
- Dispatch routines: `FatFsdCreate`, `FatFsdRead`, `FatFsdWrite`, etc.
- Fast I/O callbacks: `FatFastIoCheckIfPossible`, `FatFastQueryBasicInfo`, `FatFastLock`, etc.
- Cache callbacks: `FatAcquireFcbForLazyWrite`, `FatReleaseFcbFromReadAhead`, etc.
- Filter callback: `FatFilterCallbackAcquireForCreateSection`.

## Research Notes

`fatinit.c` is the root bootstrap for the ReactOS FastFAT driver. Most functional behavior is delegated elsewhere; this file defines how the driver becomes visible to NT I/O, cache, and filesystem-filter infrastructure. The registry reads establish compatibility defaults that influence name handling and long filename behavior throughout the driver.
