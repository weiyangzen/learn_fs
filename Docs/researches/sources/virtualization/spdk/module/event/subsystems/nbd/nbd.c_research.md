# File Research: sources/virtualization/spdk/module/event/subsystems/nbd/nbd.c

Registers the SPDK NBD service as an event subsystem.

Key elements:
- Initializes through `spdk_nbd_init()`.
- Finishes asynchronously through `spdk_nbd_fini()`.
- Writes config JSON through `spdk_nbd_write_config_json()`.
- Registers subsystem name `nbd`.

Dependencies:
- Declares dependency on `bdev`.

Research notes:
- Bridges SPDK block devices to Linux NBD lifecycle under the event framework.
