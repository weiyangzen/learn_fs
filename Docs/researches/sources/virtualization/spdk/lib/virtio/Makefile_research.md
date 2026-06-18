# File Research: sources/virtualization/spdk/lib/virtio/Makefile

## Purpose
Builds the SPDK `virtio` library.

## Key Elements
Includes SPDK common make rules, sets shared object version `9.0`, adds `$(ENV_CFLAGS)`, and compiles `virtio.c`, `virtio_vhost_user.c`, `virtio_vfio_user.c`, and `virtio_pci.c` into `LIBNAME = virtio`. Uses `spdk_virtio.map` as the map file and includes `mk/spdk.lib.mk`.

## Dependencies
Depends on the SPDK build system rooted two directories up from this Makefile.

## Behavior/Risks
All three backend transports are always listed in `C_SRCS`; platform/build conditionals, if any, must come from included SPDK make rules or source-level guards rather than this file.
