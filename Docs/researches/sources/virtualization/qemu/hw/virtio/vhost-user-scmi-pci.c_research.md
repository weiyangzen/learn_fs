# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-scmi-pci.c

## Purpose
Provides PCI transport glue for vhost-user SCMI.

## Key Behavior
- Embeds `VHostUserSCMI`.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Uses non-transitional PCI type `vhost-user-scmi-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; follows the same virtio PCI wrapper conventions.
