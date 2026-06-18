# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-vsock.c

## Purpose
Implements vhost-user vsock by combining vhost-user backend initialization with common vhost-vsock virtio logic.

## Key Behavior
- Filters backend features through a vhost-user vsock feature list, then delegates vsock-specific feature handling to common code.
- Caches `virtio_vsock_config` and returns it to the guest.
- Handles backend config-change notifications by refetching config and notifying the guest.
- Starts/stops through `vhost_vsock_common_start()` and `vhost_vsock_common_stop()` on virtio status transitions.
- Requires a `chardev`.
- Initializes vhost-user state, realizes common vsock state, registers config notifier, initializes `vhost_dev`, and fetches initial config.
- Cleans up vhost, common vsock state, and vhost-user state on unrealize or failure.
- Marks VMState unmigratable.

## Filesystem/Storage Relevance
No direct filesystem implementation, but vsock channels can support guest-host service communication used around filesystem and storage agents.
