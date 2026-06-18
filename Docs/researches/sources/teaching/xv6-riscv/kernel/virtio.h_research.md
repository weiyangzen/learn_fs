# File Research: sources/teaching/xv6-riscv/kernel/virtio.h

Defines virtio MMIO register offsets, status bits, feature bits, queue structures, descriptor flags, and block request format.

Important contents:
- Virtio MMIO offsets for device discovery, feature negotiation, queue setup, interrupts, and queue addresses.
- Status bits for acknowledge, driver, features-ok, and driver-ok.
- Block and ring feature bits intentionally negotiated away by the driver.
- `NUM` queue size.
- `struct virtq_desc`, `virtq_avail`, `virtq_used`, and `virtio_blk_req`.
- Block request types `VIRTIO_BLK_T_IN` and `VIRTIO_BLK_T_OUT`.

Filesystem relevance: defines the hardware-facing format used by `virtio_disk.c`, which provides block I/O for the buffer cache and filesystem.
