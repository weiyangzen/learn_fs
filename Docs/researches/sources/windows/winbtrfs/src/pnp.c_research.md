# File Research: sources/windows/winbtrfs/src/pnp.c

## Purpose

`pnp.c` implements WinBtrfs Plug and Play IRP handling for filesystem volumes, the root bus device, volume PDOs, and volume filter/device wrappers.

## Main Entry Point

- `drv_pnp(PDEVICE_OBJECT DeviceObject, PIRP Irp)`: dispatch routine for `IRP_MJ_PNP`.

It enters the filesystem context, manages top-level IRP state, routes by device extension type, completes handled requests, or forwards unhandled requests down the stack.

## Filesystem VCB PnP Paths

- `pnp_query_remove_device()`: checks for open root children, flushes dirty metadata with `do_write()`, frees cached trees, and returns denial or unsuccessful status.
- `pnp_remove_device()`: sends dismount notification for mounted volumes, clears `mounted_device`, marks the VCB removing, and calls `uninit()` if no files are open.
- `pnp_surprise_removal()`: marks mounted volume state as removing without flush, clears mounted-device linkage, and uninitializes if possible.
- `pnp_device_usage_notification()`: tracks paging/hibernation/dump-file usage through `Vcb->page_file_count`, then forwards to the real device.

## Bus Device Handling

- `bus_pnp()` handles bus-level PnP minor functions.
- Query/remove/start/cancel/surprise/remove are mostly success or refusal as appropriate.
- `bus_query_capabilities()` sets `UniqueID` and `SilentInstall`.
- `bus_query_device_relations()` enumerates global `pdo_list` under `pdo_list_lock`, skips `dont_report` PDOs, references each child PDO, and returns `BusRelations`.
- `bus_query_hardware_ids()` returns `ROOT\btrfs`.

## PDO Handling

- `pdo_pnp()` handles PDO-specific PnP requests.
- `pdo_query_device_id()` formats `Btrfs\{uuid}` from the PDO UUID.
- `pdo_query_hardware_ids()` returns `BtrfsVolume`.
- `pdo_query_id()` routes `BusQueryDeviceID` and `BusQueryHardwareIDs`.
- `pdo_query_device_relations()` returns a single-object `TargetDeviceRelation` for the PDO.
- `pdo_device_usage_notification()` propagates usage notifications to all child backing devices by allocating nested PnP IRPs, setting a completion routine, waiting for completion when pending, and returning the first failure.

## Locking and Lifetime

- Global PDO enumeration uses `pdo_list_lock`.
- Per-PDO child enumeration uses `pdode->child_lock`.
- Mounted filesystem state changes use `Vcb->tree_lock`.
- Device relation outputs reference returned device objects as required by PnP manager contracts.
- Nested device usage notifications use an event-backed completion context to synchronize with lower drivers.

## Dependencies

- Includes `btrfs_drv.h`.
- Uses external globals `pdo_list_lock` and `pdo_list`.
- Calls core filesystem helpers such as `has_open_children()`, `do_write()`, `free_trees()`, `uninit()`, `is_top_level()`, and logging macros.
- Uses Windows kernel PnP, IRP, device relation, and paging path APIs.

## Research Notes

- PnP support is split by device extension type: bus, volume, PDO, and actual filesystem VCB.
- Query-remove behavior is conservative and refuses removal if open children exist.
- Surprise removal intentionally avoids metadata writeback and transitions to removal state.
- Device usage propagation is important for pagefile/hibernation/dump-file correctness across multi-device Btrfs volumes.
