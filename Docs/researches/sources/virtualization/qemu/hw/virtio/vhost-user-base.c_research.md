# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-base.c

## Purpose
Implements an abstract base class for simple vhost-user virtio devices whose data path and configuration are delegated to an external daemon.

## Key Behavior
- Starts by enabling host notifiers, binding guest notifiers, setting acknowledged features, starting `vhost_dev`, and unmasking queues.
- Stops by stopping `vhost_dev`, unbinding guest notifiers, and disabling host notifiers.
- Uses virtio status transitions to start/stop the backend.
- Gets features directly from backend-advertised features, excluding the protocol feature bit.
- Optionally fetches and sets virtio config space through vhost-user config protocol.
- Installs a config notifier that raises virtio config-change interrupts.
- Realize path validates chardev and virtio ID, defaults queue count and queue size, initializes vhost-user state, initializes virtio, creates queues, initializes `vhost_dev`, and registers chardev event handlers.
- Handles chardev open by reconnecting and restoring started state.
- Handles chardev close through deferred `vhost_user_async_close()`.
- Unrealize stops, cleans up vhost, deletes queues, and releases virtio state.

## Filesystem/Storage Relevance
Many small vhost-user devices in this group subclass this base. The same pattern is useful for storage-adjacent daemons that implement virtio semantics outside QEMU.
