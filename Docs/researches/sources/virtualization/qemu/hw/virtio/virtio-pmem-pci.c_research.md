# File Research: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.c

## Purpose
PCI wrapper for the virtio persistent memory device. It adapts `VirtIOPMEM` to the virtio-pci transport and implements QEMU’s `MemoryDeviceClass` interface for memory-device management and QMP reporting.

## Main Responsibilities
- `virtio_pmem_pci_realize()` forces virtio 1.0 mode via `virtio_pci_force_virtio_1()` and realizes the embedded `VirtIOPMEM` on the virtio-pci bus.
- Implements memory-device address accessors by forwarding the address to/from the embedded pmem device’s `VIRTIO_PMEM_ADDR_PROP`.
- Exposes the underlying memory region and plugged size through the `VirtIOPMEMClass` methods.
- Fills `MemoryDeviceInfo` with `VirtioPMEMDeviceInfo`, including the PCI device ID when present and detailed pmem information from the real virtio device.
- Registers `virtio-pmem-pci` using `virtio_pci_types_register()` with parent `TYPE_VIRTIO_MD_PCI`.

## Key Integration Points
- Depends on `virtio-pmem-pci.h`, `hw/mem/memory-device.h`, and the virtio-pmem class interface.
- Uses `virtio_instance_init_common()` to construct the embedded `TYPE_VIRTIO_PMEM` object inside the PCI wrapper.
- `MemoryDeviceClass` callbacks make this PCI device visible to the same memory hotplug/reporting infrastructure as other memory devices.

## Filesystem/Storage Relevance
This is the PCI transport-facing half of virtio-pmem. It makes host-backed persistent memory available to guests as a virtio PCI memory device, with address and size exposed to QEMU’s memory-device machinery.

## Notable Constraints
- The device is forced to modern virtio 1.0; no transitional/legacy type names are registered here.
- Most semantic validation is delegated to the embedded `VirtIOPMEM` device.
