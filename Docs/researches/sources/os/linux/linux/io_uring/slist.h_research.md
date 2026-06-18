# File Research: sources/os/linux/linux/io_uring/slist.h

Internal singly linked list helpers for io_uring work queues and stacks.

Key responsibilities:
- Provides iteration macros for `io_wq_work_list`.
- Provides empty/init helpers and tail insertion.
- Supports insertion after an existing node, cutting/removing nodes, stack head insertion, stack extraction, and getting the next work item.

Important invariants:
- List head `first` is accessed with `READ_ONCE`/`WRITE_ONCE` where shared with lockless producers/consumers.
- `last` must be maintained whenever tail or final element changes.
- Stack extraction assumes `stack->next` is non-NULL.
