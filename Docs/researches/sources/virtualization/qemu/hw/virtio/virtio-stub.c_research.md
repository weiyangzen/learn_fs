# File Research: sources/virtualization/qemu/hw/virtio/virtio-stub.c

## Purpose
Build-time stub for virtio QMP commands when virtio support is disabled.

## Main Responsibilities
- Defines `qmp_virtio_unsupported()` to set `Error` text `"Virtio is disabled"` and return `NULL`.
- Implements stub versions of:
  - `qmp_x_query_virtio()`
  - `qmp_x_query_virtio_status()`
  - `qmp_x_query_virtio_vhost_queue_status()`
  - `qmp_x_query_virtio_queue_status()`
  - `qmp_x_query_virtio_queue_element()`
- Each exported QMP function returns the common unsupported error.

## Integration Points
- Includes QAPI virtio command declarations so the symbols match the real virtio QMP implementation.
- Allows QEMU builds without virtio to satisfy QMP linkage while producing clear runtime errors for virtio introspection commands.

## Filesystem/Storage Relevance
Indirect. In non-virtio builds, virtio storage/filesystem introspection commands fail through this stub instead of being unavailable at link time or crashing.
