# File Research: sources/virtualization/qemu/hw/virtio/vhost-vsock-pci.c

## Purpose
Implements the PCI transport wrapper for the `TYPE_VHOST_VSOCK` virtio device.

## Key Elements
- Defines `VHostVSockPCI`, embedding a `VirtIOPCIProxy` and a `VHostVSock` child device.
- Exposes `vectors` property with default value `3`.
- `vhost_vsock_pci_realize()` forces virtio 1 for non-legacy-check-disabled configurations to avoid migration issues on newer machine types, then realizes the child on the PCI proxy bus.
- Class init sets vendor/device IDs, PCI class `PCI_CLASS_COMMUNICATION_OTHER`, revision `0`, device category `MISC`, and the realize callback.
- Registers generic and non-transitional PCI type names.

## Dependencies
Uses QEMU virtio-pci, qdev property, QOM, PCI IDs, and `vhost-vsock.h`.

## Behavior/Risks
This is transport glue; most vsock behavior is in `vhost-vsock.c` and `vhost-vsock-common.c`. The important compatibility behavior is conditional `virtio_pci_force_virtio_1()`.
