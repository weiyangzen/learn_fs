# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/queue.h

## Scope

Complete file read, 64 lines. This header defines the DKTP queue object interface.

## Public Surface

It exports:

- `struct que_obj`: queue data pointer and operation table.
- `struct que_objops`: init, free, insert, delete callbacks, and reserved slots.
- Factory prototypes `qfifo_create()`, `qmerge_create()`, `qsort_create()`, and `qtag_create()`.
- Dispatch macros `QUE_INIT`, `QUE_FREE`, `QUE_ADD`, and `QUE_DEL`.

## Behavior And Integration

The queue object abstracts disk buffer queue policy: FIFO, merge, sorted, or tagged variants. Flow-control and target disk code call the macros without knowing the concrete queue implementation.

## Dependencies And Invariants

The interface assumes `struct que_data`, `struct buf`, and DKTP object conventions. Objects must have valid `que_data` and `que_ops`.

## Risks

Old-style factory prototypes and unchecked callback dispatch provide weak compile-time safety. Queue implementations must agree on ownership and locking of `struct que_data`.
