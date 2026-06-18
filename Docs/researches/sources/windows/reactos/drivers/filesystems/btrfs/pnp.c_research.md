# File Research: sources/windows/reactos/drivers/filesystems/btrfs/pnp.c

## Purpose

`pnp.c` implements Plug and Play IRP handling for the ReactOS/WinBtrfs driver. It covers filesystem device removal paths, a root bus device that reports Btrfs volume PDOs, PDO identity/relation handling, device usage notifications, and the top-level PnP dispatch routine.

## Filesystem Device PnP

`pnp_query_remove_device` acquires `tree_lock`, denies removal if the root fileref or descendants are open, flushes pending metadata with `do_write`, frees cached trees, then returns `STATUS_UNSUCCESSFUL`. The flush is still useful because removal may be imminent, but query-remove is effectively refused.

`pnp_remove_device` handles mounted volume removal by sending `FSRTL_VOLUME_DISMOUNT`, clearing `vde->mounted_device`, marking the VCB as removing, and calling `uninit` if no open files remain.

`pnp_surprise_removal` is similar but skips notification and just marks removal/detaches the mounted device state.

`pnp_device_usage_notification` tracks paging/hibernation/dump usage with `IoAdjustPagingPathCount` and forwards the IRP to the real device.

## Bus Device PnP

`bus_query_capabilities` marks the virtual bus as unique-id capable and silent-install capable.

`bus_query_device_relations` returns `BusRelations` for all PDOs in global `pdo_list` that are not marked `dont_report`, referencing each PDO.

`bus_query_hardware_ids` returns the multi-string `ROOT\btrfs`.

`bus_pnp` handles start/cancel/surprise/remove as success, rejects query-remove, answers capabilities, bus relations, and hardware IDs when applicable, and otherwise forwards to the attached lower device.

## PDO PnP

`pdo_query_device_id` returns a stable device id of the form `Btrfs\xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` using the PDO UUID.

`pdo_query_hardware_ids` returns `BtrfsVolume`.

`pdo_query_id` dispatches device-id and hardware-id queries.

`device_usage_completion` completes internally generated child usage IRPs.

`pdo_device_usage_notification` forwards usage notifications to each mounted child volume device object, waiting synchronously for completion and failing on the first child failure.

`pdo_query_device_relations` answers `TargetDeviceRelation` with the PDO itself.

`pdo_pnp` handles PDO query id, lifecycle minor functions, query-remove refusal, usage notification forwarding, and target-device relations.

## Top-Level Dispatch

`drv_pnp` is the `IRP_MJ_PNP` dispatch routine. It enters filesystem context, marks top-level IRP state, then routes by device extension type:

- `VCB_TYPE_BUS`: `bus_pnp`.
- `VCB_TYPE_VOLUME`: forward to attached device.
- `VCB_TYPE_PDO`: `pdo_pnp`.
- `VCB_TYPE_FS`: handle filesystem PnP minor functions locally or forward unknown minors to the real device.
- Invalid/missing extension: `STATUS_INVALID_PARAMETER`.

For filesystem VCBs it handles cancel-remove, query-remove, remove, surprise-removal, and usage notification. It completes handled IRPs itself and restores top-level IRP state before returning.

## Research Notes

This file is mostly lifecycle and identity glue around the core filesystem VCB. The intentional refusal of query-remove for filesystem, bus, and PDO paths is notable. Removal and surprise removal paths are careful to mark VCB state and uninitialize only when open-file counts allow it. Bus/PDO code allocates Windows PnP response buffers that the PnP manager owns after completion.
