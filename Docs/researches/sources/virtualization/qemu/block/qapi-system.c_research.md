# File Research: sources/virtualization/qemu/block/qapi-system.c

## Purpose
Implements QMP command handlers for block-device operations that are specific to QEMU system emulators: removable media tray handling, medium insertion/removal/change, legacy eject, I/O throttling, and block latency histogram configuration.

## Main Entry Points
- `qmp_get_blk()` resolves exactly one of QMP `device` or `id` to a `BlockBackend`.
- `qmp_blockdev_open_tray()` and `qmp_blockdev_close_tray()` open/close removable media trays.
- `qmp_blockdev_remove_medium()` removes a node from a backend.
- `qmp_blockdev_insert_medium()` inserts an existing node into a backend.
- `qmp_blockdev_change_medium()` opens a new image, opens/removes/inserts/closes media around the change.
- `qmp_eject()` opens the tray and removes the medium.
- `qmp_block_set_io_throttle()` translates QMP throttle fields into `ThrottleConfig`.
- `qmp_block_latency_histogram_set()` sets or clears latency histogram boundaries.

## Internal Mechanics
Tray opening checks removability, tray presence, tray-open state, and medium lock state. If locked and not forced, it sends an eject request and returns an in-progress error. Medium removal verifies removability/tray state for attached devices, checks block operation blockers for eject, removes the BDS from the backend, and updates device media callbacks for tray-less devices.

Medium insertion validates that the backend is removable or device-less, the tray is open when applicable, and no medium is already present. It rejects node insertion when the target node is already attached to a backend. `change-medium` derives open flags from the backend root state, applies read-only override policy, preserves detect-zeroes, opens the new image, opens the tray, removes old media, inserts the new BDS, and closes the tray.

Throttle handling fills every total/read/write BPS and IOPS bucket, optional burst maxima and burst lengths, optional IOPS size, validates the config, then enables, updates, or disables the backend throttle group. Histogram handling applies common or per-operation boundaries to read/write/zone-append/flush latency histograms.

## Dependencies
Uses QAPI block command types, `BlockBackend`, blockdev graph helpers, removable-media callbacks, throttle groups/config validation, block accounting histograms, and graph/main-loop locking.

## Filesystem/Block Relevance
This is the management-plane layer for runtime block-device media and performance controls. It connects QMP commands to QEMU block backends and block graph nodes.

## Risks and Notes
- `qmp_get_blk()` enforces exactly one of `device` and `id`; callers rely on its error shape.
- Some tray-related errors are intentionally ignored by higher-level commands for tray-less devices.
- `change-medium` must relinquish its opened image reference regardless of insertion success because the backend takes its own reference on success.
- Histogram clearing checks no common/read/write/flush boundaries, but append-specific presence is handled later in setting paths.
