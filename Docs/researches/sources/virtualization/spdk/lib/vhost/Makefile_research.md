# File Research: sources/virtualization/spdk/lib/vhost/Makefile

This Makefile builds SPDK’s vhost library.

It sets shared library version `SO_VER := 10` and `SO_MINOR := 0`, adds the current directory and environment C flags, builds `vhost.c`, `vhost_rpc.c`, `vhost_scsi.c`, `vhost_blk.c`, and `rte_vhost_user.c`, names the library `vhost`, and uses `spdk_vhost.map` as the map file.

The file delegates actual build mechanics to `mk/spdk.lib.mk`.
