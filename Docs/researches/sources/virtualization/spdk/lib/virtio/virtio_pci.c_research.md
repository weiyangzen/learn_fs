# File Research: sources/virtualization/spdk/lib/virtio/virtio_pci.c

## Purpose
Implements the modern virtio PCI backend for SPDK `virtio_dev`, including PCI enumeration/attach, BAR capability mapping, queue setup, MMIO config access, interrupt enablement, and remove-event handling.

## Key Elements
`struct virtio_hw` stores mapped PCI BARs, modern common config, device config, notify base/multiplier, ISR pointer, PCI device, owning `virtio_dev`, interrupt settings, and removal/remap state. A global tailq tracks active virtio PCI hardware under `g_hw_mutex`.

The modern backend ops read/write device config using config-generation retry, get/set 64-bit features through feature select registers, get/set status, enable MSI-X interrupts, read queue size, set up queues, delete queues, notify queues, and write JSON info/config.

Queue setup allocates a single physically contiguous 2 MiB-aligned DMA region for the vring, computes descriptor/avail/used addresses, writes queue address registers, selects MSI-X vector if interrupts are enabled, computes the notify address from notify offset and multiplier, and enables the queue.

Capability discovery walks the PCI capability list, maps vendor-specific modern virtio capability regions, records common/notify/device/ISR regions, and rejects devices missing any required modern capability. Legacy/transitional devices are detected but ignored.

Enumeration and attach wrap SPDK PCI APIs. Probe filters virtio PCI IDs, maps modern capabilities, invokes the user create callback with a `virtio_pci_ctx`, registers a SIGBUS/error handler once, and inserts successful devices into the global list. Remove-event handling supports UIO events and VFIO removed-state polling.

The SIGBUS handler remaps each mapped BAR at the same virtual address as private anonymous memory filled with `0xff` when a device disappears, so existing MMIO pointers can be read without repeated SIGBUS faults.

## Dependencies
Depends on SPDK memory, MMIO, string, env, PCI APIs from `spdk_internal/virtio.h`, Linux virtio IDs, POSIX `mmap`/`munmap`, and SPDK PCI event/error handler facilities.

## Behavior/Risks
Only modern virtio PCI devices are supported; legacy devices are explicitly ignored. Secondary process enumeration/attach is not implemented and returns without probing.

Queue memory must fit within 2 MiB and must have a valid physical address. The legacy physical-address limit check remains for non-modern devices, but normal init sets `modern = 1`.

Hot-remove handling is defensive but complex: the thread-local `g_thread_virtio_hw` must be set around MMIO operations so the SIGBUS handler knows which BARs to remap. A failed remap attempts to unmap prior remaps, leaving the device in an error path.
