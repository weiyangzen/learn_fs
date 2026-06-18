# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rng-pci.c

## Purpose
Provides PCI transport glue for vhost-user RNG.

## Key Behavior
- Embeds `VHostUserRNG`.
- Provides a `vectors` property defaulting to unspecified.
- Defaults vector count to one.
- Registers input category and PCI class `PCI_CLASS_OTHERS`.
- Uses non-transitional PCI type `vhost-user-rng-pci`.

## Filesystem/Storage Relevance
No direct filesystem behavior; follows the same vhost-user PCI model as storage wrappers.
