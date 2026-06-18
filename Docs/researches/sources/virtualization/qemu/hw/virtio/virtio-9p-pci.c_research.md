# File Research: sources/virtualization/qemu/hw/virtio/virtio-9p-pci.c

## Purpose
Implements the PCI transport wrapper for the virtio 9p filesystem device.

## Key Elements
- Defines `V9fsPCIState`, embedding `VirtIOPCIProxy` and `V9fsVirtioState`.
- `virtio_9p_pci_realize()` realizes the child `TYPE_VIRTIO_9P` device on the PCI proxy bus.
- Exposes `ioeventfd` default-on and `vectors=2` properties.
- Class init sets Red Hat virtio vendor ID, `PCI_DEVICE_ID_VIRTIO_9P`, ABI revision, storage category, and class id `0x2`.
- Registers base, generic, transitional, and non-transitional virtio-pci type names.

## Dependencies
Uses virtio-pci glue, 9p virtio device definitions, qdev properties, and QOM module registration.

## Behavior/Risks
This file is pure transport binding; 9p filesystem semantics live in the `hw/9pfs` implementation.
