# sources/storage-engines/tikv/src/storage/txn/latch.rs

## Purpose
`latch.rs` implements scheduler latches that serialize commands touching overlapping keys before they enter MVCC write processing. It is an in-memory concurrency-control structure, not an MVCC lock. Commands hash their keys into latch queues and proceed only when they are first for every required key hash.

## Important APIs, types, and functions
`Lock` is the public per-command latch request. It contains sorted deduplicated `required_hashes` and `owned_count`, with helpers `new`, `hash`, `acquired`, `force_assume_acquired`, and `is_write_lock`. `Latches` is the public latch table with `new`, `acquire`, and `release`. Internal `Latch` stores a `VecDeque<Option<(key_hash, command_id)>>` and supports `get_first_req_by_hash`, `pop_front`, `wait_for_wake`, `push_preemptive`, and queue shrinking.

## Control flow
`Lock::new` hashes all keys, sorts them, and deduplicates them to avoid deadlock and repeated acquisition. `Latches::acquire` resumes from `lock.owned_count`, locks the slot for each key hash, and checks the first queued request with that exact hash. If the current command is already first, it counts as acquired. If no matching request exists, it enqueues itself and counts as acquired. If another command is first, it enqueues itself and stops, leaving the command partially acquired.

`release` removes the current command from every owned latch and returns command IDs to wake. It can transfer a subset of latches to a next command by preemptively pushing that command to the front instead of waking waiters for those hashes. This supports command chaining while preserving ordering. The caller must ensure the releasing command is at the front.

## State and persistence behavior
All state is volatile memory under `parking_lot::Mutex` and cache-padded slots. Holes are left in queues when a non-front matching entry is removed, and `maybe_shrink` removes front holes and shrinks large queues when they become small. No disk state is touched.

## Dependencies and integration points
It depends on Rust hashing, `VecDeque`, `parking_lot`, and `crossbeam::CachePadded`. It integrates with scheduler command definitions through `gen_lock!`, which builds `Lock` objects from command keys. MVCC write commands rely on latches to serialize conflicting key operations before snapshot/write processing.

## Risks
Correctness depends on the invariant that if command A precedes command B in one overlapping latch, it precedes B in all overlapping latches. Sorting and deduplication help preserve this. Partial acquisition must be retried with the same `Lock` and command ID; misuse can leave stale queue entries. The preemptive transfer path is powerful but risky: the kept latch set must be a sorted subset of the released lock, and the next command must force or complete acquisition consistently.

## Test signals
Tests cover wakeup ordering for overlapping keys, multiple independent commands, small latch-slot counts that force hash-slot collisions, and partial release/transfer behavior for single and multiple keys with and without queued waiters. They also verify latches become empty after release sequences.
