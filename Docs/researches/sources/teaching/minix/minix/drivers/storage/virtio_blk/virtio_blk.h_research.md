# File Research: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.h

## Purpose

Provides BSD-licensed virtio-blk protocol constants and structures.

## API Surface

Defines virtio-blk feature bits, ID size, packed `struct virtio_blk_config`, request command types, barrier/flush/get-id flags, `struct virtio_blk_outhdr`, `struct virtio_scsi_inhdr`, and status byte values.

## Dependencies

Used by `virtio_blk.c` together with MINIX integer typedefs and the virtio library.

## Risks

The packed config layout and feature bit numbers must match the virtio specification. The driver reads config offsets manually, so any mismatch between this structure and manual offset assumptions would be dangerous.
