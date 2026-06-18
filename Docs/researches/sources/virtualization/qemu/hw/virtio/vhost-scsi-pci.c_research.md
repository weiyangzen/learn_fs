# File Research: sources/virtualization/qemu/hw/virtio/vhost-scsi-pci.c

## Purpose
Provides PCI transport binding for kernel `vhost-scsi`.

## Key Behavior
- Defines `vhost-scsi-pci-base` embedding `VirtIOPCIProxy` and `VHostSCSI`.
- Supports a `vectors` property defaulting to unspecified.
- Auto-selects SCSI queue count via `virtio_pci_optimal_num_queues()` when the virtio-scsi config requests automatic queues.
- Defaults MSI-X vectors to request queues plus fixed SCSI queues plus one config vector.
- Registers storage category, Red Hat virtio PCI vendor/device IDs, and SCSI class code.
- Adds a `bootindex` alias to the child vhost-scsi device.

## Filesystem/Storage Relevance
This is the PCI-facing entry point for SCSI devices accelerated through kernel vhost, allowing guest block devices to be served by a host SCSI target backend.
