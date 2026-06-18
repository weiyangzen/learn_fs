# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-snd-pci.c

## Purpose
Provides PCI transport glue for vhost-user sound.

## Key Behavior
- Embeds `VHostUserSound`.
- Forces one MSI-X vector.
- Registers sound category and multimedia audio PCI class.
- Uses non-transitional PCI type `vhost-user-snd-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; another small vhost-user PCI wrapper.
