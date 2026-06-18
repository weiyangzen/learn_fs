# File Research: sources/virtualization/qemu/hw/virtio/virtio-config-io.c

## Purpose
Provides byte/word/dword config-space read/write helpers for legacy and modern virtio config access.

## Key Elements
- Legacy helpers `virtio_config_readb/readw/readl()` bounds-check, refresh config via `get_config`, and load using host-endian unaligned helpers.
- Legacy write helpers store byte/word/dword into `vdev->config` and call `set_config` if implemented.
- Modern helpers mirror the same behavior but use little-endian accessors for 16-bit and 32-bit values.
- Out-of-range reads return `(uint32_t)-1`; out-of-range writes are ignored.

## Dependencies
Uses `hw/virtio/virtio.h` and QEMU unaligned load/store helpers.

## Behavior/Risks
The split between legacy host-endian and modern little-endian helpers is guest ABI visible. Callers rely on the simple bounds behavior for config-space holes or short accesses.
