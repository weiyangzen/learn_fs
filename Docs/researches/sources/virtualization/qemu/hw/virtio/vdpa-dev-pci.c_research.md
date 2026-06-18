# File Research: sources/virtualization/qemu/hw/virtio/vdpa-dev-pci.c

## Purpose
Provides PCI transport glue for the generic `vhost-vdpa-device`.

## Key Behavior
- Defines `vhost-vdpa-device-pci-base` embedding `VirtIOPCIProxy` plus `VhostVdpaDevice`.
- Initializes the embedded virtio device with `TYPE_VHOST_VDPA_DEVICE`.
- Exposes `bootindex` as an alias to the child vDPA device.
- During post-init, derives PCI class code and transitional device ID from the actual vDPA virtio device ID.
- Sets MSI-X vector count to `num_queues + 1`, reserving one vector for config changes.
- Registers generic, transitional, and non-transitional PCI type names.

## Filesystem/Storage Relevance
This enables PCI assignment of arbitrary vDPA virtio devices, including storage-class vDPA devices when the kernel vDPA backend exposes them.
