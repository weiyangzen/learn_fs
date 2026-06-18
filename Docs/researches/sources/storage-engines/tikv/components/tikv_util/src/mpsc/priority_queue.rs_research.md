# sources/storage-engines/tikv/components/tikv_util/src/mpsc/priority_queue.rs

## Purpose
Implements an unbounded priority-based multi-producer/multi-consumer channel where lower `u64` priority values are received first and equal priorities preserve FIFO through a sequence number.

## Important APIs, Types, and Functions
- `unbounded<T: Send>()` returns `Sender<T>` and `Receiver<T>`.
- `PriorityQueue<T>` stores a `SkipMap<MapKey, Cell<T>>`, sequence counter, sender count, and receiver count.
- `MapKey { priority, sequence }` gives sorted ordering.
- `Sender::{send,try_send}` insert values and unpark receivers.
- `Receiver::{try_recv,recv}` pop the front entry, spin briefly, then park with `parking_lot_core`.

## Control Flow
Senders reject messages when no receivers remain, insert a boxed value in a `Cell`, and unpark one waiter using the queue address. Receivers pop the lowest key from the skip map; if empty and all senders are gone they report disconnection, otherwise they spin and then park until a sender unparks or disconnection wakes all waiters. Dropping the last sender calls `unpark_all`.

## State and Persistence Behavior
All queue state is in memory. `Cell` uses an atomic pointer and `take` to move values out exactly once; its drop path releases any unconsumed value. Sender/receiver counts are atomics tied to clone/drop.

## Dependencies and Integration Points
Uses `crossbeam_skiplist::SkipMap`, `parking_lot_core` park/unpark primitives, and crossbeam channel error types for API compatibility. It is exposed as `mpsc::priority_queue`.

## Risks
The implementation relies on raw pointers in `Cell` and correct single-take semantics. `SeqCst` is used for value pointer swaps and disconnection checks, but queue length in the park validation closure is still a race-prone condition handled by the park API. Unbounded storage can grow without backpressure.

## Test Signals
Tests validate priority ordering, FIFO under equal priority via sequence, send errors after receiver drop, disconnect after sender drop, blocking receive wakeup, draining after sender drop, and multi-threaded producer/consumer sum preservation.
