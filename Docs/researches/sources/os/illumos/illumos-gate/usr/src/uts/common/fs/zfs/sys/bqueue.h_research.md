# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bqueue.h

Read status: complete, 54 lines.

Purpose: bounded blocking queue abstraction with byte-size accounting.

Key structures and APIs:
- `bqueue_t` stores a list, lock, producer/consumer condition variables, current size, max size, and node offset.
- `bqueue_node_t` supplies embedded linkage and item size.
- `bqueue_init()`, `bqueue_destroy()`, `bqueue_enqueue()`, `bqueue_dequeue()`, and `bqueue_empty()` manage queue use.

Dependencies: `zfs_context.h`.

Research notes:
- The node offset lets callers embed `bqueue_node_t` inside arbitrary payload structs.
- Queue capacity is tracked by logical item size, not just item count.
