# File Research: sources/virtualization/spdk/module/event/subsystems/vfu_tgt/Makefile

Builds the vfio-user target event subsystem library.

Key elements:
- Compiles `vfu_tgt.c`.
- Produces `event_vfu_tgt`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by parent Makefile when `CONFIG_VFIO_USER` is enabled.

Research notes:
- Optional fsdev dependency is controlled in the C source by `SPDK_CONFIG_FSDEV`.
