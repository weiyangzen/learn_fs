# File Research: sources/virtualization/spdk/lib/nvmf/Makefile

## Purpose
Build definition for the SPDK NVMe-oF target library `nvmf`.

## Main Responsibilities
- Sets SPDK root include context and common make infrastructure.
- Defines shared library version fields `SO_VER := 23` and `SO_MINOR := 0`.
- Builds core NVMf sources: controller, discovery controller, bdev command path, subsystem, RPC, transport, TCP, stubs, and mDNS server.
- Conditionally includes RDMA, DH-HMAC-CHAP authentication, vfio-user, and Fibre Channel sources.
- Adds external include/library flags for optional providers.

## Key Build Conditions
- `CONFIG_RDMA=y` adds `rdma.c` and links `-libverbs`; FreeBSD builds opportunistically add Mellanox/Chelsio provider libraries if present.
- `CONFIG_HAVE_EVP_MAC=y` adds `auth.c`, tying authentication support to OpenSSL EVP MAC availability.
- `CONFIG_VFIO_USER=y` adds `vfio_user.c`, vfio-user include/library paths, and links `-lvfio-user -ljson-c`.
- `CONFIG_FC=y` adds Fibre Channel sources and include paths.

## Storage Relevance
The file controls which NVMe-oF transport and feature modules are compiled into the target, directly affecting available storage fabrics, authentication, and vfio-user behavior.

## Risks / Notes
- Authentication code is not built unless EVP MAC support is detected.
- Optional provider linkage is platform/config dependent, so runtime capability differs across builds.
