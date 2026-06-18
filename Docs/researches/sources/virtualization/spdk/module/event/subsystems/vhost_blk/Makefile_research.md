# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_blk/Makefile

Builds the vhost block event subsystem library.

Key elements:
- Compiles `vhost_blk.c`.
- Produces `event_vhost_blk`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by the parent subsystem Makefile when vhost is enabled.

Research notes:
- Runtime dependency on bdev is declared in source.
