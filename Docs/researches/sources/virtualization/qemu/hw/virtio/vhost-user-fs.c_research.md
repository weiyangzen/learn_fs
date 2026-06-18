# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-fs.c

## Purpose
Implements QEMU's virtio-fs frontend using a vhost-user backend such as `virtiofsd`.

## Key Behavior
- Advertises virtio-fs relevant feature bits including version 1, indirect descriptors, event index, packed ring, IOMMU platform, ring reset, in-order, and notification data.
- Builds virtio config space from the filesystem tag and number of request queues.
- Validates mandatory `chardev`, non-empty `tag`, tag length, positive request queue count, power-of-two queue size, and maximum queue size.
- Initializes vhost-user state and virtio device ID `VIRTIO_ID_FS`.
- Creates one hiprio queue plus configured request queues.
- Initializes a `vhost_dev` with all virtio-fs queues.
- Starts/stops through guest notifier binding and `vhost_dev_start/stop`.
- Masks/polls guest notifiers while ignoring the special config interrupt index.
- Implements backend state save/load through `vhost_save_backend_state()` and `vhost_load_backend_state()`.
- Adds a VMState subsection for internal backend migration state and checks backend support before migration.
- Provides `chardev`, `tag`, `num-request-queues`, and `queue-size` properties.

## Filesystem/Storage Relevance
This is QEMU's virtio-fs device model: it exposes a shared host filesystem to the guest while delegating filesystem request processing to a vhost-user backend.
