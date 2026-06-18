# File Research: sources/virtualization/qemu/hw/virtio/virtio-pmem-pci.h

## Purpose
Header defining the virtio-pmem PCI wrapper type.

## Main Contents
- Includes `virtio-md-pci.h`, `virtio-pmem.h`, and QOM object helpers.
- Declares `TYPE_VIRTIO_PMEM_PCI` as `"virtio-pmem-pci-base"`.
- Defines the `VIRTIO_PMEM_PCI` instance checker.
- Defines `struct VirtIOPMEMPCI`, which embeds:
  - `VirtIOMDPCI parent_obj`
  - `VirtIOPMEM vdev`

## Design Role
The wrapper extends the memory-device-aware virtio PCI base (`VirtIOMDPCI`) rather than plain `VirtIOPCIProxy`, allowing pmem to participate in memory-device address/region reporting while still carrying an embedded virtio pmem device.

## Filesystem/Storage Relevance
This type declaration is the structural link between virtio-pci transport, QEMU memory devices, and the persistent-memory virtio backend.
