# File Research: sources/virtualization/spdk/app/vhost/Makefile

This makefile builds the legacy/specific `vhost` application from `vhost.c`. It includes SPDK common rules and module definitions, sets `APP = vhost`, and links a broad module set: `$(ALL_MODULES_LIST)`, the event framework, vhost block, vhost SCSI, and NBD event modules.

When using SPDK's in-tree DPDK environment, it adds `env_dpdk_rpc`. On Linux with `CONFIG_VFIO_USER=y`, it adds `event_vfu_tgt`. With `CONFIG_FSDEV=y`, it adds `event_fsdev`.

The build uses the standard C app make include and standard install/uninstall macros. Compared with `spdk_tgt`, this app links vhost-specific event modules unconditionally in the base library list, making it a vhost-oriented target wrapper.
