# File Research: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.h

## Purpose
Declares the `VhostIOVATree` interface used by vhost-vDPA and shadow virtqueue code.

## Key API
- Constructor/destructor: `vhost_iova_tree_new()`, `vhost_iova_tree_delete()`.
- Autoptr cleanup registration for GLib-managed cleanup.
- HVA-oriented lookup/allocation/removal: `find_iova`, `map_alloc`, `remove`.
- GPA-oriented lookup/allocation/removal: `find_gpa`, `map_alloc_gpa`, `remove_gpa`.

## Filesystem/Storage Relevance
This header exposes the mapping API needed for vhost shadow queues to translate guest storage or filesystem request buffers into backend-visible IOVA addresses.
