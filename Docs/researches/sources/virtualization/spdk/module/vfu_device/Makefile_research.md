# File Research: sources/virtualization/spdk/module/vfu_device/Makefile

Builds the vfio-user virtio device module as library `vfu_device`.

Key contents:
- Sets `SPDK_ROOT_DIR` to the SPDK root relative to `module/vfu_device`.
- Includes `mk/spdk.common.mk`.
- Declares shared object version `SO_VER := 5` and minor `SO_MINOR := 0`.
- Always builds:
  - `vfu_virtio.c`
  - `vfu_virtio_blk.c`
  - `vfu_virtio_scsi.c`
  - `vfu_virtio_rpc.c`
- Adds `vfu_virtio_fs.c` only when `CONFIG_FSDEV=y`.
- Uses `mk/spdk_blank.map`.
- Includes `mk/spdk.lib.mk`.

Role:
- This Makefile defines the compilation boundary for common virtio-over-vfio-user code, block and SCSI device models, RPC glue, and optional virtio-fs support.
