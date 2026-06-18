# sources/test-tools/fio/io_u_queue.h

## Purpose
Defines lightweight queue containers used to manage free and requeued `io_u` pointers.

## Important APIs, Types, and Functions
`struct io_u_queue` is a LIFO stack with `io_us`, `nr`, and `max`. Inline functions `io_u_qpop`, `io_u_qpush`, `io_u_qempty`, and `io_u_qiter` operate on it. `struct io_u_ring` is a circular FIFO with `head`, `tail`, `max`, and `ring`, operated by `io_u_rpush`, `io_u_rpop`, and `io_u_rempty`. Allocation functions are declared for both queue types.

## Control Flow
Free `io_u` objects are pushed/popped from the stack queue. Requeued partial or deferred units are pushed to and popped from the ring in FIFO order.

## State and Persistence Behavior
All state is in memory. The inline operations assert on overflow but otherwise do not allocate or persist anything.

## Dependencies and Integration Points
Includes `assert.h`, `stddef.h`, and fio `lib/types.h`. Used directly by `io_u.c` and thread-data setup.

## Risks
The queue is not internally synchronized; callers must use thread-data locks when needed. Overflow handling is an assertion, so release builds may not catch misuse cleanly depending on assert configuration.

## Test Signals
Focused queue tests for empty/full behavior, ordering, iterator behavior, and async-lock callers are useful. fio runtime depth tests indirectly exercise this code.
