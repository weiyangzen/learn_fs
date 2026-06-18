# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.c

## Scope

This file implements the kernel disk conditioner used to simulate slower storage behavior on a per-mount basis. It delays I/O, constrains mount I/O limits, tracks simulated HDD seek/spin-up behavior, and restores original mount fields on disable or unmount.

## Public And Internal APIs Covered

- `disk_conditioner_delay()` computes and applies synthetic delay for buffer I/O.
- `disk_conditioner_get_info()` returns current conditioner settings.
- `disk_conditioner_set_info()` enables, disables, or updates settings after root and entitlement checks.
- `disk_conditioner_unmount()` restores and frees conditioner state.
- `disk_conditioner_mount_is_ssd()` reports effective SSD/HDD behavior.
- Internal helpers save and restore mount I/O fields.

## Control Flow And Behavior

`disk_conditioner_set_info()` requires root plus `com.apple.private.dmc.set`. It lazily allocates per-mount conditioner state, snapshots original read/write/segment/queue fields, clamps requested limits to hardware-advertised mount limits, updates mount throttling fields while enabled, and resets throttle periods.

`disk_conditioner_delay()` exits unless the vnode, mount, and enabled conditioner state are available. HDD mode estimates seek cost from block distance since the last I/O and adds spin-up latency after long idle periods. SSD mode uses the full block range as the access-time scale. Throughput caps add read or write transfer delay. Existing elapsed time is subtracted before calling `delay()`.

## State And Data Structures

- `struct _disk_conditioner_info_t` embeds public `disk_conditioner_info`, saved mount fields, last block number, and last I/O timestamp.
- State is attached to `mp->mnt_disk_conditioner_info`.
- Mount fields affected include max read/write byte counts, segment counts, I/O queue depth, and I/O scale.

## Dependencies

Depends on buffer/vnode/mount internals, `fsctl` conditioner structures, IOKit entitlement checking, kauth credentials, time helpers, and mount throttling reset via `throttle_info_mount_reset_period()`.

## Risks And Invariants

- Saved mount fields must be restored exactly when disabling and during unmount.
- Delay math depends on `BLK_MAX(mp)` and device block sizing; invalid or zero sizing would be hazardous.
- The delay loop asserts the remaining delay fits in `INT_MAX`.
- `disk_conditioner_get_info()` returns success even when no conditioner state exists, leaving caller-provided output unchanged.
- Mount mutation is protected with `mount_lock()`, while delay reads conditioner state locklessly on the I/O path.
