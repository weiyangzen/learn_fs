<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/state.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/state.rs

Purpose: `state.rs` defines the per-object lock state and the packed atomic state machine used by fast shared/exclusive lock acquisition.

Important APIs/types/functions: `AtomicLockState` packs writer flag, reader count, reader-waiter count, and writer-waiter count into a `u64`, plus a `last_accessed` timestamp. It exposes fast-path availability, shared/exclusive acquisition/release, waiting-counter increment/decrement, free/waiter checks, access timestamp, and test-only waiter count accessors. `ObjectLockState` combines `AtomicLockState`, traditional `Notify` fields, `OptimizedNotify`, owner metadata locks, and priority. `ExclusiveOwnerInfo` and `SharedOwnerEntry` track owners, acquired time, counts, and timeout. Object-level methods acquire/release shared/exclusive locks, inspect lock status, and derive current mode.

Control flow: fast shared acquisition requires no writer and no waiting writers, then increments reader count up to 255. Exclusive acquisition requires state exactly zero and sets writer flag. Object-level acquisition first updates atomic state, then records owner metadata under parking_lot locks. Shared release removes/decrements owner metadata first, then releases one atomic reader and notifies a writer if no shared owners remain. Exclusive release verifies owner, clears writer flag, clears owner metadata, and notifies one writer if waiting writers exist, otherwise all readers.

State and persistence behavior: state is in-memory and cache-line aligned. Atomic bit layout supports at most 255 concurrent readers and 65535 waiting readers/writers. Owner metadata is separate from atomic state, so consistency depends on acquisition/release methods updating both. Timestamps use `SystemTime` and second precision for idle cleanup. Lock TTL is stored in owner metadata and used for monitoring expiry, but this file does not itself auto-expire held locks.

Dependencies and integration points: used by `LockShard` for all actual locking, by `ObjectStatePool` for reset/reuse, and by `ObjectLockInfo` generation. It depends on `parking_lot`, `smallvec`, `tokio::sync::Notify`, `OptimizedNotify`, `LockMode`, and `LockPriority`.

Risks: object-level acquisition modifies atomic state before owner metadata; if a panic occurred while holding metadata locks, atomic and owner state could diverge. Release attempts to roll back shared-owner metadata if atomic release fails, but the correction is necessarily best-effort. Reentrant shared locks by the same owner increment an owner count; reentrant exclusive locks are not supported. The 255-reader cap is encoded in eight bits and can become a scalability limit. Writer preference is implemented by blocking new readers when writers are waiting; leaked writer-waiting counters can starve readers.

Test signals: unit tests cover atomic shared/exclusive transitions and object-level shared/exclusive ownership. Shard cancellation tests cover waiting counters after aborted futures. Additional tests should assert owner metadata consistency on repeated shared acquisitions by the same owner, reader cap behavior, writer-preference fairness, and TTL/expiry reporting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/state.rs -->
