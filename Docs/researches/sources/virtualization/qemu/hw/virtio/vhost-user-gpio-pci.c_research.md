# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-gpio-pci.c

## Purpose
Provides PCI transport glue for the vhost-user GPIO virtio device.

## Key Behavior
- Embeds `VHostUserGPIO` in a `VirtIOPCIProxy`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-gpio-pci`.

## Filesystem/Storage Relevance
No direct filesystem behavior; follows the same vhost-user PCI wrapper pattern used by storage and filesystem frontends.
