# File Research: sources/os/bsd/netbsd-src/sys/sys/bufq_impl.h

## Scope

Defines internal buffer queue strategy state and registration support.

## APIs And Data Structures

- Kernel-only header.
- `struct bufq_state` stores strategy callbacks: put, get, cancel, fini, private data, flags, and selected strategy.
- `bufq_private()` returns strategy-private storage.
- `buf_inorder()` compares buffers by cylinder plus raw block or by raw block only; treats `NULL` as after any non-NULL buffer and returns false for equal ordering.
- `struct bufq_strat` stores strategy name, init function, priority, refcount, and SLIST linkage.
- `BUFQ_DEFINE()` declares static strategy descriptors.
- Declares `bufq_register` and `bufq_unregister`.

## Dependencies

- Depends on `struct buf` fields and `BUFQ_SORT_*` constants from `bufq.h`.

## Risks And Invariants

- `buf_inorder()` asserts at least one operand is non-NULL.
- Strategy registration state includes refcounts, so unload paths must coordinate with active queues.
