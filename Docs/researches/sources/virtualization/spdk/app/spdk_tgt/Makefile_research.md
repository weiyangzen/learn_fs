# File Research: sources/virtualization/spdk/app/spdk_tgt/Makefile

This makefile builds the `spdk_tgt` application from `spdk_tgt.c`. It sets `SPDK_ROOT_DIR` to two directories above the app, includes SPDK common make definitions and module definitions, and uses `mk/spdk.app.mk` for application build rules.

The library list is intentionally broad. It starts from `$(ALL_MODULES_LIST)`, then explicitly adds the event framework and the iSCSI and NVMe-oF event modules. If the configured environment is SPDK's in-tree DPDK environment, it adds `env_dpdk_rpc` so the target can expose DPDK environment RPCs.

Linux-specific modules are conditional. On Linux it adds `event_nbd`; when `CONFIG_UBLK=y`, it adds `event_ublk`; when `CONFIG_VHOST=y`, it adds `event_vhost_blk` and `event_vhost_scsi`; when `CONFIG_VFIO_USER=y`, it adds `event_vfu_tgt`. Separately, `CONFIG_FSDEV=y` adds `event_fsdev`.

The install and uninstall targets delegate to the standard `$(INSTALL_APP)` and `$(UNINSTALL_APP)` macros. Overall, this file defines `spdk_tgt` as the general SPDK target binary that links the enabled storage frontends/backends into one event-framework executable.
