# File Research: sources/virtualization/qemu/hw/virtio/virtio-qmp.h

## Purpose
Public header for virtio QMP helper functions.

## Main Contents
- Includes QAPI virtio types plus core virtio and vhost headers.
- Declares:
  - `qmp_find_virtio_device(const char *path)`
  - `qmp_decode_status(uint8_t bitmap)`
  - `qmp_decode_protocols(uint64_t bitmap)`
  - `qmp_decode_features(uint16_t device_id, const uint64_t *bitmap)`

## Integration Role
Allows other virtio QMP command implementations to reuse canonical path resolution and bitmap decoding logic instead of duplicating map traversal and QAPI object construction.

## Filesystem/Storage Relevance
Supports introspection for virtio storage and filesystem-adjacent devices by exposing decoded status and feature information to QMP command code.
