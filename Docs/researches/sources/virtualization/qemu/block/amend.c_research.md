# File Research: sources/virtualization/qemu/block/amend.c

This file implements the QMP `x-blockdev-amend` job path for changing image-format options through a block job.

Key structures and functions:
- `BlockdevAmendJob` embeds `Job`, stores cloned `BlockdevAmendOptions`, the target `BlockDriverState`, and the `force` flag.
- `blockdev_amend_run()` runs under graph read lock, sets job progress to one unit, invokes the format driver's `bdrv_co_amend()`, updates progress, and frees the cloned options.
- `blockdev_amend_pre_run()` calls optional driver-specific `bdrv_amend_pre_run()`.
- `blockdev_amend_free()` calls optional `bdrv_amend_clean()` under graph read lock and unreferences the target BDS.
- `qmp_x_blockdev_amend()` validates node lookup, driver lookup, whitelist rules, driver immutability, and amend support, then creates and starts a manual-dismiss amend job.

Concurrency and graph model:
- QMP setup uses `GRAPH_RDLOCK_GUARD_MAINLOOP()`.
- The actual job run uses `GRAPH_RDLOCK_GUARD()`.
- Cleanup takes the graph read lock in the main loop before invoking driver cleanup.

Filesystem/block relevance:
- This is a format-maintenance control path, not data-plane I/O.
- It exposes driver-specific image option mutation while using QEMU's job framework for async execution, progress, lifecycle, and failure reporting.

Potential pitfalls:
- The command rejects changing the block driver; the option driver must match `bs->drv`.
- Driver support is mandatory through `.bdrv_co_amend`.
- `options` are cloned into the job; caller-owned QAPI options are not consumed directly by the job.
