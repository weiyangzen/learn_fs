# File Research: sources/virtualization/qemu/hw/virtio/virtio-blk-pci.c

## Purpose
Implements the PCI transport wrapper for the virtio block device.

## Key Elements
- Defines `VirtIOBlkPCI`, embedding `VirtIOPCIProxy` and `VirtIOBlock`.
- Exposes `class`, default-on `ioeventfd`, and `vectors` properties.
- `virtio_blk_pci_realize()` chooses an optimal queue count when `num_queues` is automatic and defaults MSI-X vectors to `num_queues + 1`.
- Class init marks the device as storage, installs PCI-specific qdev property handling, sets Red Hat virtio block PCI IDs, ABI revision, and default class `PCI_CLASS_STORAGE_SCSI`.
- Instance init creates the child `TYPE_VIRTIO_BLK` and aliases `bootindex`.
- Registers base, generic, transitional, and non-transitional virtio-pci type names.

## Dependencies
Uses virtio-pci, virtio-blk config, qdev PCI property helpers, and QOM.

## Behavior/Risks
This is transport glue; queue count and vector defaults affect guest-visible interrupt layout and migration compatibility.
