# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-test-device-pci.c

## Purpose
Provides PCI transport glue for the configurable vhost-user test device.

## Key Behavior
- Embeds `VHostUserBase` directly.
- Forces one MSI-X vector.
- Registers input category and communication-other PCI class.
- Initializes the child device as `TYPE_VHOST_USER_TEST_DEVICE`.
- Uses non-transitional PCI type `vhost-user-test-device-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; useful for prototyping arbitrary vhost-user backends, including storage experiments.
