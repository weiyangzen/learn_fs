# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-scmi.c

## Purpose
Implements the vhost-user SCMI virtio device with custom lifecycle logic rather than subclassing `VHostUserBase`.

## Key Behavior
- Advertises selected feature bits including version 1, notify-on-empty, indirect descriptors, event index, ring reset, and `VIRTIO_SCMI_F_P2A_CHANNELS`.
- Does not support `VIRTIO_SCMI_F_SHARED_MEMORY`.
- Starts by enabling host notifiers, binding guest notifiers, acknowledging features, starting vhost, and unmasking queues.
- Tracks `started_vu` because generic started-state checks are not sufficient for all stop paths.
- Refuses status transitions when the chardev/backend is not connected.
- Handles chardev open/close by toggling `connected` and restoring/stopping state.
- Creates command and event virtqueues, each size 256.
- Initializes `vhost_dev` with two queues and `VHOST_BACKEND_TYPE_USER`.
- Cleans up queues, vhost-user state, and virtio state on failure or unrealize.
- Marks VMState unmigratable.

## Filesystem/Storage Relevance
No direct filesystem role; useful contrast with `VHostUserBase` because it manually implements the same vhost-user lifecycle pieces.
