# File Research: sources/virtualization/spdk/module/bdev/daos/bdev_daos.h

This header declares the public management functions for the DAOS bdev module. `create_bdev_daos()` creates a bdev from name, UUID, DAOS pool/container labels, optional object class, block count, and block size, returning the registered `spdk_bdev`. `delete_bdev_daos()` unregisters by name with an SPDK bdev unregister callback. `bdev_daos_resize()` grows a DAOS bdev to a new size in MiB.

All DAOS connection, DFS object, event queue, and IO details remain private to `bdev_daos.c`.
