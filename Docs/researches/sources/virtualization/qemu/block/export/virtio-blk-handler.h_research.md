# File Research: sources/virtualization/qemu/block/export/virtio-blk-handler.h

## Purpose
Defines the shared virtio-blk export handler interface used by transport-specific export drivers.

## Contents
- Includes `system/block-backend.h`.
- Defines virtio sector constants:
  - `VIRTIO_BLK_SECTOR_BITS = 9`
  - `VIRTIO_BLK_SECTOR_SIZE = 512`
- Defines maximum discard and write-zeroes sector counts, both `32768`.
- Defines `VirtioBlkHandler`:
  - `BlockBackend *blk`
  - `char *serial`
  - `uint32_t logical_block_size`
  - `bool writable`
- Declares:
  - `virtio_blk_process_req(...)`

## Role
Provides a transport-neutral contract: frontends supply virtqueue iovecs and handler configuration, and the implementation performs virtio-blk command decoding and backend I/O.
