# File Research: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal_rpc.c

This file exposes OPAL management through JSON-RPC. It registers RPCs to initialize OPAL ownership, revert the TPer, create/delete OPAL range bdevs, query range info, set lock state, and create new users.

`bdev_nvme_opal_init` validates the NVMe controller exists and has an OPAL device, takes ownership with the supplied password, then activates the locking SP. It maps `-EBUSY` and `-EACCES` to clearer error messages. `bdev_nvme_opal_revert` validates the controller and calls `spdk_opal_cmd_revert_tper()`, with a TODO noting OPAL vbdevs should be deleted before revert.

`bdev_opal_create` decodes controller name, NSID, locking range ID, start, length, and password, calls `vbdev_opal_create()`, and returns an OPAL bdev name derived from controller/NSID/range ID. `bdev_opal_get_info` returns name, range start/length, read/write lock enablement, and current read/write lock state from `spdk_opal_locking_range_info`.

`bdev_opal_delete` calls `vbdev_opal_destruct()`, which secure-erases and resets the range. `bdev_opal_set_lock_state` forwards user ID, password, and string lock state. `bdev_opal_new_user` enables a user, sets its password, and grants range permissions through `vbdev_opal_enable_new_user()`.

The file is a thin adapter; semantic constraints such as supported NSID, valid lock-state strings, range setup, and OPAL command ordering are enforced in `vbdev_opal.c` and the SPDK OPAL library.
