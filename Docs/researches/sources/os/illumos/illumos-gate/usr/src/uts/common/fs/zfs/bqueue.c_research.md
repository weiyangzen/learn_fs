# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bqueue.c

## Scope

Implements a bounded blocking queue whose capacity is measured in caller-supplied item-size units rather than element count.

Read completely: 111 lines.

## Main APIs

- `bqueue_init()` initializes the embedded list, add/pop condition variables, mutex, node offset, size, and maximum size.
- `bqueue_destroy()` asserts the queue is empty and destroys synchronization primitives and list state.
- `bqueue_enqueue()` blocks until enough capacity exists, stores the item size in the embedded queue node, inserts at tail, and signals consumers.
- `bqueue_dequeue()` blocks until nonempty, removes the head item, subtracts its size, and signals producers.
- `bqueue_empty()` returns whether current used capacity is zero.

## Data Model

Queued objects must embed a `bqueue_node_t` at the offset supplied to `bqueue_init()`. `obj2node()` computes the embedded node address for a queued object.

## Dependencies

Uses illumos `list_t`, condition variables, mutexes, assertions, and caller-managed item storage.

## Invariants And Risks

- `item_size` must be greater than zero and less than `bq_maxsize`.
- Capacity accounting depends on each dequeued object’s embedded `bqn_size`.
- `bqueue_empty()` reads `bq_size` without taking the lock, so callers needing a synchronized answer must externally serialize.
- Destroy requires no queued items and no blocked producers/consumers.
