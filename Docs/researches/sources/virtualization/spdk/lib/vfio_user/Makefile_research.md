# File Research: sources/virtualization/spdk/lib/vfio_user/Makefile

This Makefile is the top-level build glue for SPDK’s `lib/vfio_user` subtree.

It sets `SPDK_ROOT_DIR` to two directories above the current directory, includes `mk/spdk.common.mk`, declares `DIRS-y += host`, and makes `all` and `clean` recurse into that subdirectory through `mk/spdk.subdirs.mk`.

The file does not build sources directly; it delegates the library build to `lib/vfio_user/host/Makefile`.
