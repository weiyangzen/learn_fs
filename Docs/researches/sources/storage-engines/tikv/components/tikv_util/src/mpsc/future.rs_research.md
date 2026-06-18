# sources/storage-engines/tikv/components/tikv_util/src/mpsc/future.rs

## Purpose
Implements an async-aware MPSC channel whose receiver is a `futures::Stream`, with bounded/unbounded queues, configurable wake policy, timeout receive, and batch-stream adaptation.

## Important APIs, Types, and Functions
- `WakePolicy::{Immediately,TillReach(usize)}` controls when senders wake the receiver.
- `Sender<T>::send` and `send_with` push into the queue and wake according to policy.
- `Receiver<T>` implements `Stream<Item=T>`, plus `try_recv` and `recv_timeout`.
- `unbounded(policy)` and `bounded(cap, policy)` construct channels.
- `BatchReceiver<T,I,C>` wraps a receiver and emits collected batches up to `max_batch_size`.

## Control Flow
The channel stores a raw pointer to a heap-allocated `Queue<T>`, with a bitfield-like `liveness` counter tracking sender and receiver presence. Sending first checks receiver liveness, pushes into `SegQueue` or `ArrayQueue`, then wakes immediately or once queue length reaches a threshold. The receiver polls by popping first, registering its waker if empty, retrying to avoid lost wakeups, and returning `None` when no senders remain.

## State and Persistence Behavior
State is entirely in memory: queue contents, `AtomicWaker`, and liveness counter. The heap queue is manually freed when the last sender/receiver side drops. `BatchReceiver` owns its receiver and collector closures.

## Dependencies and Integration Points
Uses `crossbeam::queue::{SegQueue,ArrayQueue}`, `futures::{Stream,AtomicWaker}`, and `crate::future::block_on_timeout`. It complements the synchronous MPSC wrapper in `mpsc/mod.rs`.

## Risks
Raw-pointer lifetime management and manual liveness arithmetic are the main safety risks. `WakePolicy::TillReach` improves batching but can delay messages until a threshold or disconnect wake. Bounded sends fail if the `ArrayQueue` is full, and wake is currently attempted even when push fails.

## Test Signals
Tests cover threshold wake behavior, immediate wake behavior, batch collection, sender/receiver wake transitions on disconnect, drop semantics for queued values, and bounded queue overflow.
