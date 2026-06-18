# File Research: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/vfu_tgt.c

Registers the vfio-user target as an event subsystem.

Key elements:
- Initializes with `spdk_vfu_init()`.
- Finishes with `spdk_vfu_fini()`.
- Registers subsystem name `vfio_user_target`.

Dependencies:
- Declares dependencies on bdev and scsi.
- Adds dependency on fsdev when `SPDK_CONFIG_FSDEV` is defined.

Research notes:
- This subsystem exposes SPDK devices through vfio-user target infrastructure.
