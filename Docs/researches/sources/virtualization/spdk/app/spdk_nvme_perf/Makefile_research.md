# File Research: sources/virtualization/spdk/app/spdk_nvme_perf/Makefile

## Purpose
Builds `spdk_nvme_perf`, SPDK's NVMe performance benchmark application.

## Main Contents
- Sets `APP = spdk_nvme_perf`.
- Compiles `perf.c`.
- Links socket modules, NVMe, VMD, keyring file support, trace, and event libraries.
- On Linux, links `-laio` and defines `HAVE_LIBAIO`.
- Uses SPDK app make infrastructure and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, VMD, socket modules, keyring file module, trace, event framework, and Linux libaio when built on Linux.

## Filesystem/Block Relevance
Builds SPDK's direct NVMe benchmark tool for measuring block I/O performance across PCIe and fabrics transports.

## Risks and Notes
- Linux builds gain libaio support through conditional flags.
- Actual benchmark behavior is implemented in `perf.c`, which is outside this grouped work item.
