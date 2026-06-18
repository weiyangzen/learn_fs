# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.c

Provides the public wrapper layer over DPDK PCI/private-ABI access. It selects a version-specific function table at runtime based on `rte_version()` and forwards all PCI/device/bus operations through that table.

Important behavior:
- Supports DPDK 21.11+ through selected 22.07 or 22.11 compatibility tables.
- Maps DPDK 22.11 ABI implementation to later supported 23.x, 24.x, 25.x, and 26.03 releases when the private ABI is considered unchanged.
- Rejects unsupported DPDK versions with `-EINVAL`.
- Wraps mem resources, device names/devargs/address/ID/NUMA, config read/write, driver registration, interrupts, bus scan/probe, and generic device devargs/name/scan-allowed helpers.

Dependency boundary: this file prevents the rest of SPDK env PCI code from directly depending on a specific DPDK private struct layout.
