# File Research: sources/virtualization/spdk/lib/virtio/virtio_vfio_user.c

## Purpose
Implements a vfio-user backed virtio transport for SPDK `virtio_dev`, presenting a remote vfio-user PCI device through the common virtio backend ops.

## Key Elements
`struct virtio_vfio_user_dev` stores the vfio-user device context, socket path, and offsets/lengths for common config, device-specific config, and notifications inside a PCI BAR.

Backend ops access device config, status, features, queue size, and queue setup through `spdk_vfio_user_pci_bar_access`. Queue setup allocates DMA vring memory, uses IOVA=VA addressing, writes descriptor/avail/used queue address registers, reads queue notify offset, and enables the queue. Queue deletion disables the queue and frees vring memory. Notify is a no-op because the implementation assumes polling.

Initialization validates name/path, constructs the common `virtio_dev`, opens the vfio-user connection with `spdk_vfio_user_setup`, enables PCI bus mastering and disables INTx in the PCI command register, and hardcodes a modern virtio layout in BAR4.

## Dependencies
Depends on SPDK memory, vfio-user PCI helpers, `spdk_internal/virtio.h`, Linux `vfio.h`, and POSIX path access.

## Behavior/Risks
The PCI capability layout is hardcoded rather than discovered: BAR4 offsets 0x0 common config, 0x1000 ISR, 0x2000 device config, and 0x3000 notifications. The comment marks capability iteration as future work, so incompatible vfio-user layouts will fail or behave incorrectly.

Queue deletion does not clear descriptor/avail/used addresses, only disables the queue and frees memory. Notify does not write doorbells, so this transport relies on the remote side polling.
