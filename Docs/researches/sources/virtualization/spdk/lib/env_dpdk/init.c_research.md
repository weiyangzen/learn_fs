# File Research: sources/virtualization/spdk/lib/env_dpdk/init.c

Builds and runs DPDK EAL initialization for SPDK. `spdk_env_opts_init()` fills defaults for name, core mask, shared memory id, memory size, main core, memory channels, base virtual address, and newer option fields guarded by `opts_size`.

`build_eal_cmdline()` constructs DPDK argv from SPDK env options. It handles program name, single-process `--no-shconf`, mutually exclusive core mask vs lcore map, core-mask-to-core-list conversion, memory channels/size, no-huge validation, NUMA enforcement, main lcore, no-pci/vtophys disable, hugepage unlink/single-file/hugedir options, PCI allow/block lists, default telemetry/log-level suppression, IOVA-mode selection, base virtual address, match-allocation, file prefix/proc type, VF token, and user-supplied `env_context` tokenization.

Linux/x86 helpers inspect `/proc/cpuinfo` and Intel IOMMU capability sysfs files to decide whether VA IOVA is safe; otherwise SPDK forces PA mode. PowerPC Linux also forces PA mode. No-huge mode forces legacy memory and VA IOVA and requires a configured memory size.

`spdk_env_init()` initializes OpenSSL config handling, prints the SPDK/DPDK versions and EAL arguments, calls `rte_eal_init()` with a copied argv because DPDK mutates it, determines legacy memory mode, then runs post-init hooks for PCI, memory maps, and vtophys. Reinitialization after SPDK-owned init only refreshes PCI state. Finalization tears down vtophys, memory map, PCI state, and generated EAL arguments; a high-priority destructor calls `rte_eal_cleanup()` only when SPDK initialized DPDK itself.
