# File Research: sources/virtualization/qemu/hw/virtio/vhost-vsock.c

## Purpose
Implements the concrete kernel vhost-vsock virtio device, including guest CID validation, backend fd acquisition, vhost initialization, status-driven start/stop, and VMState hooks.

## Key Elements
- `vhost_vsock_get_config()` writes the guest CID into `virtio_vsock_config`.
- `vhost_vsock_set_guest_cid()` and `vhost_vsock_set_running()` call backend-specific vhost-vsock ops.
- `vhost_vsock_set_status()` starts vhost when virtio status says the device should run, then sets backend running state; stop clears running and stops common vhost state.
- `vhost_vsock_device_realize()` validates `guest-cid > 2` and 32-bit range, obtains either monitor-provided `vhostfd` or `/dev/vhost-vsock`, makes it nonblocking, realizes common queues, initializes a kernel vhost backend, and sets guest CID.
- VMState uses common pre-save and post-load callbacks to ensure backend quiescence and transport reset.
- Properties are `guest-cid` and optional `vhostfd`.

## Dependencies
Uses Linux virtio-vsock headers, QEMU socket/fd monitor helpers, qdev properties, common vhost-vsock code, and generic kernel vhost backend initialization.

## Behavior/Risks
- Reserved CIDs `0`, `1`, and `2` are rejected.
- If `qemu_set_blocking(vhostfd, false)` fails after opening `/dev/vhost-vsock`, this function returns without the later vhost cleanup path; callers should be aware of fd lifetime assumptions around early failures.
- `set_status()` logs backend start/stop failures but returns `0`, matching virtio set-status callback expectations.
