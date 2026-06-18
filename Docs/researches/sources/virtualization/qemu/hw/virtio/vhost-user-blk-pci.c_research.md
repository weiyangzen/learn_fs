# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-blk-pci.c

## Purpose
Provides PCI transport binding for `vhost-user-blk`.

## Key Behavior
- Embeds `VHostUserBlk` inside a `VirtIOPCIProxy`.
- Exposes `class` and `vectors` PCI properties.
- Auto-selects queue count when `num_queues` requests automatic mode.
- Defaults vector count to number of queues plus one config vector.
- Registers storage category, virtio block PCI device ID, SCSI storage class code, and transitional/non-transitional type names.
- Adds `bootindex` alias to the child block device.

## Filesystem/Storage Relevance
This is the PCI frontend for block devices implemented by a vhost-user daemon, commonly used to move block I/O processing outside QEMU.
