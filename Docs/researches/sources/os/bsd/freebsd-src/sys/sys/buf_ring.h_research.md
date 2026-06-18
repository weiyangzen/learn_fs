# File Research: sources/os/bsd/freebsd-src/sys/sys/buf_ring.h

## Purpose
`buf_ring.h` implements a power-of-two circular pointer ring used by performance-sensitive queues such as network driver transmit queues.

## Main Interfaces
- `struct buf_ring` stores producer and consumer head/tail indexes, masks, sizes, drop count, optional debug lock, and flexible ring storage.
- `buf_ring_enqueue()` is multi-producer safe.
- `buf_ring_dequeue_mc()` is multi-consumer safe.
- `buf_ring_dequeue_sc()`, `buf_ring_advance_sc()`, `buf_ring_putback_sc()`, `buf_ring_peek()`, and `buf_ring_peek_clear_sc()` are single-consumer or lock-protected operations.
- `buf_ring_full()`, `buf_ring_empty()`, and `buf_ring_count()` inspect state.
- Kernel and userland allocation/free variants are provided.

## Implementation Notes
Head and tail counters are only masked when indexing, leaving high bits as an epoch to reduce ABA-style wrap confusion. Atomic acquire loads and release stores enforce ordering between data publication and tail advancement. Multi-party operations spin until prior operations complete in order.

## Dependencies and Constraints
Ring size must be a power of two. Single-consumer functions assume external serialization. Debug mode checks duplicate enqueues, dangling entries, and lock ownership.
