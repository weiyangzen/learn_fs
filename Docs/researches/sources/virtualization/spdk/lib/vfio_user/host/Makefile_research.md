# File Research: sources/virtualization/spdk/lib/vfio_user/host/Makefile

This Makefile builds the SPDK vfio-user host library.

It sets `SPDK_ROOT_DIR` to three directories above the current directory, includes common SPDK make settings, sets shared library version `SO_VER := 7` and `SO_MINOR := 0`, builds `vfio_user_pci.c` and `vfio_user.c`, names the library `vfio_user`, and points `SPDK_MAP_FILE` at `spdk_vfio_user.map`.

The file finishes by including `mk/spdk.lib.mk`, so normal SPDK library rules own compilation, linking, and install metadata.
