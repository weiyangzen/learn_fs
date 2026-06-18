# File Research: sources/virtualization/spdk/lib/nbd/nbd_rpc.c

JSON-RPC layer for SPDK NBD exports.

Key RPCs:
- `nbd_start_disk`: decodes `bdev_name` and optional `nbd_device`; if no device is provided, scans `/dev/nbdN` and `/sys/block/nbdN/pid` for an available device. Starts the export and returns the chosen NBD path.
- `nbd_stop_disk`: validates an active `nbd_device`, spawns a detached pthread to call `NBD_DISCONNECT`, and returns boolean success.
- `nbd_get_disks`: returns all active exports or one requested export, with `nbd_device` and `bdev_name`.

Key helpers:
- `check_available_nbd_disk` validates `/dev/nbd<num>` syntax, rejects devices already registered in SPDK, and treats existing sysfs pid files as busy.
- `find_available_nbd_disk` scans sequential NBD device names.
- `rpc_start_nbd_done` retries automatic device assignment on `-EBUSY`.

Dependencies:
- SPDK JSON-RPC, env/string/util/log, RPC autogen contexts, Linux NBD path conventions, internal NBD helpers.

Research notes:
- Stop RPC intentionally delegates disconnect ioctl to a pthread because it can block while data flushes.
- Automatic device assignment is Linux-specific and depends on `/dev/nbd*` and `/sys/block/nbd*/pid`.
- Scope relevance: management-plane entry point for exposing SPDK bdevs to kernel NBD consumers.
