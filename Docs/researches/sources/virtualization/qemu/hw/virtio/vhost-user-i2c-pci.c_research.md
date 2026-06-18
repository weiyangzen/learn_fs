# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-i2c-pci.c

## Purpose
Provides PCI transport glue for the vhost-user I2C virtio device.

## Key Behavior
- Embeds `VHostUserI2C` inside a `VirtIOPCIProxy`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-i2c-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; shares the vhost-user PCI frontend pattern used by other virtio devices.
