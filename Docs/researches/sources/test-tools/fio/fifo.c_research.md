# sources/test-tools/fio/fifo.c

## Purpose
`fifo.c` implements a small circular byte FIFO used by fio internals. It is derived from a kernel-style FIFO implementation and provides allocation, free, put, and get operations.

## Important APIs, Types, And Functions
`fifo_alloc(size)` allocates `struct fifo` plus a byte buffer and initializes `in`/`out` counters. `fifo_free()` releases both. `fifo_put()` writes up to available room, splitting the copy at the physical end of the ring. `fifo_get()` reads or discards up to available bytes, also handling wraparound, then resets both counters to zero when empty.

## Control Flow
Put computes `len = min(requested, fifo_room(fifo))`, copies the first segment to `buffer + (in & (size - 1))`, copies any wrapped remainder to the start of the buffer, and advances `in`. Get computes available length from `in - out`, optionally copies out the first and wrapped segments, advances `out`, and normalizes empty state.

## State And Persistence
State is the allocated buffer and monotonically increasing `in`/`out` counters. Data is volatile and not thread-safe. Empty normalization prevents unbounded counter growth across repeated full drains.

## Dependencies And Integration Points
The code depends on `fifo.h` and `minmax.h`. It assumes the FIFO size is a power of two because it uses `index & (size - 1)` rather than `% size`.

## Risks
`fifo_alloc()` does not check the second `malloc`; if buffer allocation fails, later use or `fifo_free()` can misbehave. No validation enforces power-of-two size. Pointer arithmetic on `void *buffer`/`void *buf` is a GNU C extension, not portable ISO C. There is no locking.

## Test Signals
Unit tests should cover power-of-two sizes, wraparound put/get, partial put when full, discard get with NULL buffer, empty counter reset, non-power-of-two misuse, and buffer allocation failure handling.
