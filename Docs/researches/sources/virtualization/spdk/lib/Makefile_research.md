# File Research: sources/virtualization/spdk/lib/Makefile

This is the top-level SPDK library directory makefile. It includes common make settings and library dependency definitions, then builds subdirectories through `mk/spdk.subdirs.mk`.

The always-enabled library directories include core SPDK infrastructure and storage subsystems: `bdev`, `blob`, `conf`, `dma`, `accel`, `event`, `json`, `jsonrpc`, `log`, `lvol`, `rpc`, `sock`, `thread`, `trace`, `util`, `nvme`, `vmd`, `nvmf`, `scsi`, `ioat`, `ut_mock`, `iscsi`, `notify`, `init`, `trace_parser`, `keyring`, and `ae4dma`.

Linux builds add `nbd`, `ftl`, and `vfio_user`; `CONFIG_UBLK=y` adds `ublk`. Unit-test support is conditional: `ut` is built only when either `CONFIG_TESTS` or `CONFIG_UNIT_TESTS` is enabled. Other feature gates add `env_ocf`, `idxd`, `vhost`, `virtio`, RDMA libraries (`rdma_cm`, `rdma_provider`, `rdma_utils`), `vfu_tgt`, and filesystem-device libraries (`fsdev`, `fuse_dispatcher`).

When `CONFIG_RDMA_PROV` is `mlx5_dv`, the `mlx5` directory is included. The makefile also detects whether `CONFIG_ENV` points to an in-tree library directory under `lib`; if so, it adds that environment directory, while out-of-tree env implementations are expected to be built separately.

The file declares `all`, `clean`, and every enabled subdir as phony, then delegates recursive build behavior to `spdk.subdirs.mk`. It is a build graph coordinator rather than a code-bearing module.
