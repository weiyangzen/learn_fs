# File Research: sources/virtualization/spdk/lib/nvme/Makefile

Build definition for SPDK's NVMe library.

Key contents:
- Sets `SPDK_ROOT_DIR` to `../..` and includes common SPDK make rules.
- Declares shared library version `SO_VER := 18`, `SO_MINOR := 1`.
- Builds the main NVMe library from controller, namespace, PCIe, TCP, fabric, discovery, poll group, auth, ZNS, KV, Opal, utility, and stub source files.
- Conditionally includes:
  - `nvme_cuse.c` when `CONFIG_NVME_CUSE=y`
  - `nvme_vfio_user.c` when `CONFIG_VFIO_USER=y`
  - `nvme_rdma.c` when `CONFIG_RDMA=y`
- Adds `-libverbs` for RDMA; on FreeBSD, conditionally links mlx4/mlx5/cxgb4 provider libraries if present.
- Adds `-lfuse3` and `_FILE_OFFSET_BITS=64` for CUSE.
- Adds `-Wpointer-arith`.
- Uses `spdk_nvme.map` as the symbol map and includes `mk/spdk.lib.mk`.

Research notes:
- This file is build orchestration only; no runtime NVMe logic is present here.
- Scope relevance is high: it selects the transport implementations that back SPDK NVMe block and virtualization integrations, including RDMA and VFIO-user.
