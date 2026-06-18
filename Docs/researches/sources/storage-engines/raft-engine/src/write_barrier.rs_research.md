# sources/storage-engines/raft-engine/src/write_barrier.rs

Purpose: this file implements a low-level write-group barrier. Concurrent callers enqueue `Writer`s; exactly one leader receives a `WriteGroup` containing a linked list of writers to process, while followers wait until their leader has set outputs.

Important APIs and types: `Writer<P, O>` wraps a mutable payload pointer, output slot, sync flag, entered time, and performance context diff. `Writer::new`, `mut_payload`, `set_output`, and `finish` are the caller-facing methods. `WriteGroup` exposes `iter_mut` over grouped writers and calls `leader_exit` on drop. `WriterIter` walks the intrusive linked list. `WriteBarrier<P, O>` has `enter` as the public synchronization method. `WriteBarrierInner` stores head/tail, pending leader, and pending condition-variable index.

Control flow: the first writer entering an empty barrier becomes leader immediately. Later writers append themselves to the current linked list. If another pending leader already exists, they wait on the follower condvar for that future group and return `None` after being processed. If no pending leader exists, the arriving writer becomes the leader of the next group and waits on `leader_cv`; when awakened it receives a group from its node through the current tail. Dropping a `WriteGroup` calls `leader_exit`, which wakes the next pending leader and the followers of the just-finished group, or clears head/tail and wakes current followers when no next leader exists.

State and persistence behavior: all state is in memory. Writers contain raw pointers into caller-owned payloads and must not outlive those payloads. Outputs are stored back into each writer by the leader and consumed by each caller with `finish`.

Dependencies and integration points: depends on `parking_lot` `Mutex`/`Condvar`, `fail` for a `leader_exit` failpoint, and `PerfContext`. It is used by the engine write path to batch concurrent writes and carry sync/performance metadata through the group leader.

Risks and invariants: this module relies on unsafe intrusive pointers and explicit caller discipline: the original payload must not be accessed while the writer exists, and every writer must remain stack-valid while linked/waiting. `WriteGroup` drop is essential for progress; leaking it would block future groups. The two follower condvars are alternated by `pending_index`; off-by-one errors would wake the wrong generation. `finish` panics if no output was set.

Test signals: `test_sequential_groups` checks single-writer groups and output propagation. `test_parallel_groups` orchestrates multiple waves of threads, validates one leader per group, verifies grouped payload/output processing, and exercises follower/leader handoff with condition variables.
