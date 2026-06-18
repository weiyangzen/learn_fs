# File Research: sources/virtualization/spdk/lib/env_dpdk/pci.c

Implements SPDK's DPDK-backed PCI environment layer. It owns global PCI driver/device/provider registries, maps DPDK `rte_pci_device` objects into `spdk_pci_device`, and provides SPDK-facing APIs for enumeration, explicit attach/detach, BAR mapping, config-space access, interrupts, claims, address parsing/formatting, and device allowlisting.

Important behavior:
- Maintains `g_pci_devices`, `g_pci_hotplugged_devices`, `g_pci_drivers`, and `g_pci_device_providers` under `g_pci_mutex`.
- Uses delayed `rte_devargs` allow/block policy to avoid immediately probing newly seen devices during scans.
- Handles DPDK hotplug remove events with deferred alarm callbacks and `pending_removal`/`removed` state.
- Registers SPDK PCI drivers with DPDK through the compatibility wrappers from `pci_dpdk.h`.
- For VFIO/IOMMU builds, maps BAR memory into the IOMMU on `spdk_pci_device_map_bar()` and unmaps on BAR unmap.
- Linux claim/unclaim uses `/var/tmp/spdk_pci_lock_<bdf>` files plus `fcntl` locks and stored PID.

Filesystem/storage relevance: this is the low-level device discovery and lifetime layer for SPDK PCI-backed storage devices such as NVMe, IOAT/IDXD DMA engines, VMD, and virtio block/SCSI.

Concurrency and lifecycle notes:
- `spdk_pci_device_detach()` clears attachment, calls the provider detach callback, and then cleans removed/hotplugged queues.
- `spdk_pci_enumerate()` first enumerates known unattached devices, then scans/probes the DPDK bus, then cleans hotplug results.
- `pci_env_fini()` only reports devices still attached; it does not forcibly detach them.
