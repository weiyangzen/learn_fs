# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-scsi-pci.c

## Purpose
Provides PCI transport binding for vhost-user SCSI.

## Key Behavior
- Embeds `VHostUserSCSI` inside `VirtIOPCIProxy`.
- Exposes a `vectors` property.
- Auto-selects queue count when virtio-scsi requests automatic queues.
- Defaults vector count to request queues plus fixed SCSI queues plus one config vector.
- Registers storage category, virtio SCSI PCI IDs, and SCSI storage class.
- Adds `bootindex` alias to the child vhost-user SCSI device.
- Registers generic, transitional, and non-transitional PCI types.

## Filesystem/Storage Relevance
This is the PCI frontend for a vhost-user SCSI backend, allowing guest SCSI block devices to be served by an external daemon.
