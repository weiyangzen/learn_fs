# File Research: sources/virtualization/qemu/block/monitor/block-hmp-cmds.c

## Purpose
Implements human monitor protocol commands for block device management, block jobs, NBD server control, qemu-io access, and informational block/snapshot output. Most commands translate HMP arguments into QMP calls or block-layer helpers.

## Main Entry Points
- `hmp_drive_add()` and `hmp_drive_add_node()` hot-add legacy drives or node-owned block graphs.
- `hmp_drive_del()` removes a node or legacy drive/backend after checking blockers and ownership.
- `hmp_commit()`, `hmp_drive_mirror()`, `hmp_drive_backup()`, `hmp_block_stream()`, and block job control functions call the corresponding block job/QMP operations.
- `hmp_snapshot_blkdev*()` and `hmp_info_snapshots()` handle external/internal snapshots and snapshot listing.
- `hmp_nbd_server_start()`, `hmp_nbd_server_add()`, `hmp_nbd_server_remove()`, and `hmp_nbd_server_stop()` manage QEMU’s NBD export server.
- `hmp_block_resize()`, `hmp_block_set_io_throttle()`, `hmp_eject()`, and `hmp_change_medium()` adapt HMP arguments to QMP block device commands.
- `hmp_qemu_io()` runs qemu-io commands against a named backend, qdev block backend, or node.
- `hmp_info_block()`, `hmp_info_blockstats()`, and `hmp_info_block_jobs()` format query results for the monitor.

## Internal Mechanics
The command handlers parse `QDict` monitor arguments, build QAPI structs such as `DriveMirror`, `DriveBackup`, `NbdServerAddOptions`, and `BlockIOThrottle`, then delegate to QMP/block APIs. Informational functions call QMP query commands and print user-facing summaries through `monitor_printf()`.

`hmp_qemu_io()` is the most unusual path: it may operate directly on an existing `BlockBackend`, or create a temporary backend for a node. Its comments explicitly document incomplete permission restoration because qemu-io commands can change permissions and issue asynchronous operations whose lifetime extends beyond the monitor command.

Snapshot listing builds per-image queues of snapshot entries, detects snapshots present on all disks, prints global snapshots, then prints partial non-loadable snapshots per image.

## Dependencies
Uses monitor/HMP infrastructure, QMP block and block-export commands, QAPI block types, block backend and graph APIs, qemu-io command support, socket parsing, QemuOpts, machine defaults, snapshot APIs, and monitor formatting helpers.

## Risks and Notes
Most functions are compatibility adapters, so behavioral correctness depends on the underlying QMP command. `hmp_drive_del()` distinguishes node deletion from legacy drive deletion and refuses unsupported deletion of blockdev-add devices through the legacy path. `hmp_qemu_io()` deliberately leaves some permissions extended, which is a known tradeoff for legacy monitor semantics and asynchronous qemu-io behavior. `hmp_nbd_server_start -a` starts the server first, then exports all inserted block devices, and stops the server again if adding any export fails.
