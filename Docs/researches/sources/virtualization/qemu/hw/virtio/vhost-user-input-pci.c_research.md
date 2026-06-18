# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-input-pci.c

## Purpose
Provides PCI transport binding for vhost-user input devices.

## Key Behavior
- Defines concrete PCI type `vhost-user-input-pci`.
- Inherits from `TYPE_VIRTIO_INPUT_PCI`.
- Embeds `VHostUserInput` and initializes it as `TYPE_VHOST_USER_INPUT`.
- Registers the type with `virtio_pci_types_register()`.

## Filesystem/Storage Relevance
No direct filesystem role; it is another vhost-user transport wrapper.
