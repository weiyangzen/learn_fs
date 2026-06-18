# File Research: sources/os/bsd/openbsd-src/sys/sys/queue.h

Defines intrusive collection macros for singly-linked lists, lists, simple queues, XOR simple queues, tail queues, and singly-linked tail queues.

Key contents:
- Debug invalidation support under `QUEUE_MACRO_DEBUG` or kernel diagnostic builds.
- `SLIST_*` heads, entries, accessors, foreach/safe iteration, insert, remove.
- `LIST_*` doubly-linked forward-list macros with O(1) removal.
- `SIMPLEQ_*` singly-linked queue with head/tail pointer.
- `XSIMPLEQ_*` queue using a random XOR cookie to obscure stored pointers.
- `TAILQ_*` doubly-linked tail queue with forward/reverse iteration, insert, remove, replace, concat.
- `STAILQ_*` singly-linked tail queue declarations and operations.

Risk notes:
- These are macro-only intrusive data structures; callers are responsible for valid membership and correct field names.
- XOR simple queues require `arc4random_buf()` availability where initialized.
