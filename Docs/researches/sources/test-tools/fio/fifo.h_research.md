# sources/test-tools/fio/fifo.h

## Purpose
`fifo.h` declares fio's circular byte FIFO interface and its small inline helpers.

## Important APIs, Types, And Functions
`struct fifo` contains `unsigned char *buffer`, `size`, `in`, and `out`. Public functions are `fifo_alloc`, `fifo_put`, `fifo_get`, and `fifo_free`. `fifo_len()` returns `in - out`, and `fifo_room()` returns `size - in + out`.

## Control Flow
The header supplies only declarations and inline arithmetic. Implementation in `fifo.c` updates `in` and `out`; callers use the inline helpers to check occupancy and capacity.

## State And Persistence
The struct stores volatile in-memory FIFO state. It has no ownership metadata beyond the buffer pointer and no synchronization fields.

## Dependencies And Integration Points
This header is self-contained for the struct and API declarations. Consumers must link with `fifo.c` and obey the implementation's power-of-two size assumption.

## Risks
The API accepts unsigned `size` without documenting or enforcing power-of-two requirements in the header. `fifo_room()` relies on `in >= out` monotonic behavior and unsigned arithmetic. There is no const-correctness for `fifo_put` input buffers.

## Test Signals
Header-level tests should compile multiple consumers, verify inline length/room arithmetic after representative operations, and document expected behavior for empty/full states.
