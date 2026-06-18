# File Research: sources/virtualization/qemu/hw/virtio/vhost-vsock-common.c

## Purpose
Provides the abstract shared implementation for vhost-vsock virtio devices. It handles common feature filtering, queue creation, vhost start/stop, guest notifier masking, and migration post-load transport reset behavior.

## Key Elements
- `feature_bits` exposes `VIRTIO_VSOCK_F_SEQPACKET`, ring reset, and packed ring filtering through generic vhost feature negotiation.
- `vhost_vsock_common_get_features()` implements `seqpacket=on/off/auto` behavior and errors if forced seqpacket is unsupported.
- `vhost_vsock_common_start()` enables vhost host notifiers, binds guest notifiers through the virtio bus, starts the backend, and unmasks all vhost queues.
- `vhost_vsock_common_stop()` stops the backend, unbinds guest notifiers, and disables host notifiers.
- `vhost_vsock_common_send_transport_reset()` injects a `VIRTIO_VSOCK_EVENT_TRANSPORT_RESET` event into the event virtqueue after migration.
- `vhost_vsock_common_realize()` creates receive, transmit, and event queues, with only the event queue owned by QEMU.
- Class init marks the type abstract, exposes the `seqpacket` property, and installs guest notifier and `get_vhost` hooks.

## Dependencies
Uses `virtio_vsock.h`, `virtio-bus`, generic `vhost`, QEMU iovec helpers, monitor infrastructure, and QOM properties.

## Behavior/Risks
- Migration pre-save asserts that the vhost backend is stopped so it cannot continue writing guest memory.
- Post-load transport reset is deferred through a virtual clock timer so virtqueue changes occur after migration completes.
- Config interrupt index is explicitly ignored in guest notifier mask/pending callbacks.
- Start error paths unwind guest and host notifier setup in reverse order.
