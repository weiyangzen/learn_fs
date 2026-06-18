# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_blk/vhost_blk.c

Registers SPDK vhost block as an event subsystem.

Key elements:
- Initializes through `spdk_vhost_blk_init()`.
- Finishes through `spdk_vhost_blk_fini()`.
- Writes config JSON through `spdk_vhost_blk_config_json()`.
- Registers subsystem name `vhost_blk`.

Dependencies:
- Declares dependency on `bdev`.

Research notes:
- Provides block-device vhost target lifecycle integration.
