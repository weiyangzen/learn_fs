# File Research: sources/teaching/xv6-public/ide.c

Implements a simple PIO IDE disk driver.

Key behavior:
- Initializes IDE lock, enables IDE IRQ through IOAPIC, waits for disk 0, probes disk 1, and switches back to disk 0.
- Maintains a linked request queue of `struct buf` objects under `idelock`.
- `idestart` programs IDE ports for read/write or multi-sector commands depending on `BSIZE`.
- `ideintr` completes the active request, reads data for reads, marks buffers valid/non-dirty, wakes sleepers, and starts the next queued request.
- `iderw` appends a locked buffer to the queue and sleeps until it becomes valid and not dirty.

Important interactions:
- Requires caller to hold the buffer sleeplock.
- Enforces `FSSIZE` block bounds.
- Uses `B_DIRTY` to decide write vs read and buffer wakeup state.
