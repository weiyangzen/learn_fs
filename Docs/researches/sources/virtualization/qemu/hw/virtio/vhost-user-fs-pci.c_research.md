# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-fs-pci.c

## Purpose
Provides PCI transport glue for virtio-fs over vhost-user.

## Key Behavior
- Embeds `VHostUserFS` inside a `VirtIOPCIProxy`.
- Provides a `vectors` property defaulting to unspecified.
- Defaults vector count to request queues plus two extra vectors for config change and hiprio queue.
- Registers as storage category with `PCI_CLASS_STORAGE_OTHER`.
- Uses only a non-transitional PCI type name, `vhost-user-fs-pci`.
- Adds `bootindex` alias to the child filesystem device.

## Filesystem/Storage Relevance
This is the PCI attachment for virtio-fs, the most directly filesystem-related device in this group.
