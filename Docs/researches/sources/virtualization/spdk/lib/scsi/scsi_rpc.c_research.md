# File Research: sources/virtualization/spdk/lib/scsi/scsi_rpc.c

This small file registers the `scsi_get_devices` JSON-RPC method.

The RPC rejects any parameters, begins a JSON array result, iterates the fixed `SPDK_SCSI_MAX_DEVS` device table returned by `scsi_dev_get_list()`, skips unallocated entries, and emits objects containing `id` and `device_name`. The method is registered for runtime use with `SPDK_RPC_REGISTER`.

The RPC intentionally exposes only basic SCSI device inventory, not LUNs, ports, bdev names, reservation state, or task state. Its correctness depends on `scsi_dev_get_list()` returning the global fixed-size device array expected by the loop.
