# File Research: sources/virtualization/qemu/hw/virtio/virtio-rng-pci.c

## Purpose
PCI wrapper for the virtio random number generator device.

## Main Responsibilities
- Defines `VirtIORngPCI`, embedding `VirtIOPCIProxy` and `VirtIORNG`.
- Provides PCI wrapper properties:
  - `ioeventfd`, default enabled.
  - `vectors`, default unspecified.
- `virtio_rng_pci_realize()` defaults unspecified MSI-X vector count to `2`, then realizes the embedded `VirtIORNG` on the virtio-pci bus.
- Class initialization sets device category, PCI vendor/device IDs, revision, class ID, transport realization callback, and properties.
- Instance initialization constructs the embedded `TYPE_VIRTIO_RNG`.
- Registers generic, transitional, and non-transitional PCI type names.

## Integration Points
- Uses generic `virtio_pci_types_register()` for QOM type registration.
- Relies on the core `virtio-rng.c` implementation for actual entropy handling.
- Sets legacy PCI device ID `PCI_DEVICE_ID_VIRTIO_RNG` for transitional compatibility.

## Filesystem/Storage Relevance
Not filesystem-specific, but shares the same virtio-pci transport machinery used by storage devices. It is useful as a compact example of a simple virtio PCI wrapper.
