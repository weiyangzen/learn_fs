# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-vsock-pci.c

## Purpose
Provides PCI transport binding for vhost-user vsock.

## Key Behavior
- Embeds `VHostUserVSock` inside `VirtIOPCIProxy`.
- Provides a `vectors` property defaulting to 3.
- Forces virtio 1.0 mode because older compatibility handling is not needed here.
- Registers misc category, virtio vsock PCI device ID, and communication-other PCI class.
- Registers generic and non-transitional PCI type names.

## Filesystem/Storage Relevance
No direct filesystem role, though vsock is often used as a guest-host communication channel adjacent to filesystem daemons and agents.
