# File Research: sources/virtualization/spdk/module/bdev/nvme/Makefile

This Makefile builds the SPDK `bdev_nvme` library. It includes the common SPDK make rules, sets shared-object version `9.0`, and declares the core C sources as `bdev_nvme.c`, `bdev_nvme_rpc.c`, `nvme_rpc.c`, and `bdev_mdns_client.c`.

Build composition is configuration- and OS-dependent. `bdev_nvme_cuse_rpc.c` is included only when `CONFIG_NVME_CUSE` is enabled, and OPAL virtual bdev support (`vbdev_opal.c`, `vbdev_opal_rpc.c`) is included only on Linux. The module uses `spdk_bdev_nvme.map` as its symbol map and finishes through `mk/spdk.lib.mk`.

This file is important for feature availability: CUSE RPCs and OPAL RPCs may not exist in all builds even though their sources are present.
