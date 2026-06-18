# File Research: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.h

## Purpose
Declares the shadow virtqueue data structures and public API.

## Main Types
- `SVQDescState`: stores the original `VirtQueueElement` and number of descriptors exposed to the backend.
- `VhostShadowVirtqueueOps`: optional owner callback for custom available-buffer handling.
- `VhostShadowVirtqueue`: owns the shadow vring, host/guest event notifiers, original virtqueue pointer, virtio device, IOVA tree, descriptor state, descriptor free-list backup, callback hooks, and ring indices.

## Key API
- Feature validation and free-slot reporting.
- Add/push/poll data path functions.
- Kick/call fd setup and vring address/area-size accessors.
- Start/stop lifecycle and allocation/free helpers with GLib autoptr support.

## Filesystem/Storage Relevance
This API is the contract used by vhost-vDPA code to interpose QEMU-managed virtqueue translation and migration support in front of backend devices.
