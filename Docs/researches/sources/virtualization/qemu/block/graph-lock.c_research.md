# File Research: sources/virtualization/qemu/block/graph-lock.c

## Purpose
Implements QEMU block graph locking: a reader/writer mechanism protecting block graph topology mutations such as adding/removing nodes and edges.

## Main State
- `graph_lock`: dummy lock object used for thread-safety analysis annotations.
- `aio_context_list_lock`: protects the list of AioContext graph-lock counters and orphaned reader count.
- `has_writer`: atomic flag indicating a writer is active or trying to become active.
- `wrlock_quiesced_counter`: tracks write locks taken through drained sections.
- `orphaned_reader_count`: preserves reader counts when an AioContext is unregistered while readers exist.
- `reader_queue`: coroutine queue for graph readers waiting on a writer.
- `BdrvGraphRWlock`: per-AioContext reader counter plus list linkage.

## AioContext Registration
- `register_aiocontext()` allocates a per-context `BdrvGraphRWlock` and inserts it into the global list.
- `unregister_aiocontext()` transfers its reader count to `orphaned_reader_count`, removes it, and frees it.
- `reader_count()` sums orphaned readers plus all per-context atomic reader counts.

## Writer Lock
`bdrv_graph_wrlock()`:
- Global-state, non-coroutine only.
- Drains all block devices when not already in a quiesced write-lock section.
- Alternates `has_writer` off while polling to avoid deadlock with callbacks that need read locks.
- Sets `has_writer = 1`, uses a memory barrier, and loops until total reader count is zero.
- Ends the temporary drain after lock acquisition when applicable.

`bdrv_graph_wrlock_drained()`:
- Begins a drained section first, increments `wrlock_quiesced_counter`, then takes the write lock.

`bdrv_graph_wrunlock()`:
- Clears `has_writer` under `aio_context_list_lock`.
- Wakes all queued readers.
- Polls bottom halves on the main AioContext so scheduled graph cleanup can run.
- Ends a drained section if the write lock was acquired through the drained helper.

## Reader Lock
`bdrv_graph_co_rdlock()`:
- Coroutine-only.
- Increments the current AioContext reader count.
- Uses a memory barrier before checking `has_writer`.
- Fast path proceeds when no writer is active.
- Slow path synchronizes with writer/unlock using `aio_context_list_lock`, decrements its reader count, kicks waiters, and sleeps on `reader_queue`.

`bdrv_graph_co_rdunlock()`:
- Decrements the reader count with release semantics.
- Uses a memory barrier and always calls `aio_wait_kick()` because a writer may be polling with `has_writer` temporarily cleared.

## Main-Loop Read Lock Stubs
- `bdrv_graph_rdlock_main_loop()` and `bdrv_graph_rdunlock_main_loop()` assert global-state, non-coroutine context.
- In this implementation, main-loop readability is effectively asserted rather than counted.

## Assertions
- `assert_bdrv_graph_readable()` checks, in debug graph-lock builds, that the caller is either in the main thread or there is an active reader.
- `assert_bdrv_graph_writable()` requires main thread and `has_writer`.

## Concurrency Notes
The design avoids cacheline bouncing by keeping reader counters per AioContext, while writer acquisition pays the cost of summing all counters. The orphaned-reader mechanism prevents counter loss when coroutines migrate or AioContexts are deleted.
