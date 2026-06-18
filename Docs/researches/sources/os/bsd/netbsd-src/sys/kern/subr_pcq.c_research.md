# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pcq.c

## Purpose
Implements a lockless producer/consumer queue for many concurrent producers and a caller-serialized single consumer.

## Main Entry Points
- `pcq_create()` allocates a queue with up to `PCQ_MAXLEN` slots.
- `pcq_destroy()` frees the queue.
- `pcq_put()` reserves and publishes an item.
- `pcq_peek()` reads the next item without consuming it.
- `pcq_get()` consumes the next published item.
- `pcq_maxitems()` returns the configured capacity.

## Control Flow And State
`struct pcq` stores `pcq_nitems`, a packed 32-bit producer/consumer cursor `pcq_pc`, and a flexible array of item slots separated onto cache lines. The low 16 bits hold the producer cursor and the high 16 bits hold the consumer cursor.

`pcq_put()` CAS-loops on `pcq_pc` to reserve the next producer position, returns false if advancing would collide with the consumer, and then publishes the item with `atomic_store_release`. `pcq_get()` snapshots cursors, returns NULL if empty or if a producer reserved but has not yet published the item, consumes the item by clearing the slot, issues a producer barrier, and CAS-loops to advance the consumer cursor. `pcq_peek()` uses a consume load of the item slot.

## Dependencies
Uses NetBSD atomics, memory barriers, kmem allocation, and queue definitions from `<sys/pcq.h>`.

## Risks And Notes
The concurrency proof depends on the release/consume ordering and the explicit `membar_producer()` before publishing the updated consumer cursor. Multiple consumers are not supported; callers must serialize `pcq_get()`. A transient NULL from `pcq_get()` can mean a producer has reserved a slot but not published yet, so users must rely on the producer's later notification path to retry.
