# File Research: sources/virtualization/qemu/hw/virtio/virtio-balloon-pci.c

## Purpose
Implements the PCI transport wrapper for the virtio balloon device.

## Key Elements
- Defines `VirtIOBalloonPCI`, embedding `VirtIOPCIProxy` and `VirtIOBalloon`.
- Exposes default-on `ioeventfd` and `vectors` defaulting to `DEV_NVECTORS_UNSPECIFIED`.
- `virtio_balloon_pci_realize()` defaults unspecified vectors to `2`, sets PCI class code to `PCI_CLASS_OTHERS`, and realizes the child balloon device.
- Instance init creates the child `TYPE_VIRTIO_BALLOON` and adds PCI-level aliases for `guest-stats` and `guest-stats-polling-interval`.
- Registers base, generic, transitional, and non-transitional PCI type names.

## Dependencies
Uses virtio-pci, qdev property, `virtio-balloon.h`, QAPI error handling, and QOM aliases.

## Behavior/Risks
Transport-only file. The property aliases are important because management tooling can access balloon stats through the PCI device.
