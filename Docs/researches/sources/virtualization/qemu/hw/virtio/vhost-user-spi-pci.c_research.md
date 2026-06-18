# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-spi-pci.c

## Purpose
Provides PCI transport glue for vhost-user SPI.

## Key Behavior
- Embeds `VHostUserSPI`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-spi-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; same transport pattern as other small vhost-user devices.
