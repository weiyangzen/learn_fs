# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/dev.c

Implements block-device access workers for `hjfs`.

Key points:
- Maintains global linked list `devs`.
- `newdev()` opens a backing file read/write, determines size in filesystem blocks, initializes hash sentinels and work queue, starts a device worker, and links the device globally.
- Rejects zero-length device files.
- `devwork()` waits on the device work queue.
- For write requests:
  - zeroes a 4096-byte block buffer
  - packs the `Buf`
  - writes one full block at `off * BLOCK`
- For read requests:
  - reads a full block, tolerating short read loops
  - unpacks into the `Buf`
- Reports bounds errors and I/O errors through `b->error`.
- Treats a work item with `b->d == nil` as a sync acknowledgement request.

Dependencies and interactions:
- Work is queued by `buf.c`.
- Uses `pack()`/`unpack()` from `conv.c`.

Research relevance:
- The I/O backend connecting `hjfs` typed buffers to a flat block device file.
