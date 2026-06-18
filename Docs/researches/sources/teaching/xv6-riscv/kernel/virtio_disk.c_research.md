# File Research: sources/teaching/xv6-riscv/kernel/virtio_disk.c

Implements the QEMU virtio block device driver used as xv6’s disk.

Important behavior:
- `virtio_disk_init()` validates the MMIO device, negotiates features, allocates descriptor/avail/used rings, configures queue 0, and marks the driver ready.
- Maintains descriptor free state, used index, per-request status, and associated `struct buf`.
- `alloc_desc()`, `free_desc()`, `free_chain()`, and `alloc3_desc()` manage descriptor lifecycle.
- `virtio_disk_rw()` builds a three-descriptor block request, publishes it to the avail ring, notifies the device, sleeps until completion, then frees descriptors.
- `virtio_disk_intr()` acknowledges interrupts, processes used-ring completions, verifies status, clears `b->disk`, and wakes sleepers.

Filesystem relevance: this is the physical block I/O endpoint below `bio.c`. All filesystem reads/writes eventually pass through this driver.
