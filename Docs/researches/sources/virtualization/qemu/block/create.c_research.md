# File Research: sources/virtualization/qemu/block/create.c

Implements the QMP `blockdev-create` command as a QEMU job. `BlockdevCreateJob` stores the target `BlockDriver` and cloned `BlockdevCreateOptions`.

`qmp_blockdev_create()` resolves the driver from the QAPI enum, enforces whitelist policy, checks that `.bdrv_co_create` exists, creates a manual-dismiss `JOB_TYPE_CREATE` job in the main AioContext, clones the options, and starts it. `blockdev_create_run()` sets one unit of progress, calls the driver's `bdrv_co_create()`, marks progress complete, frees the cloned options, and returns the driver result.
