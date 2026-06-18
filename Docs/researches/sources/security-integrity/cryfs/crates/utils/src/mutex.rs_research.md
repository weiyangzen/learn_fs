# sources/security-integrity/cryfs/crates/utils/src/mutex.rs

Purpose: helper for locking two `Arc<Mutex<T>>` values in stable pointer order to avoid deadlock from inconsistent lock ordering.

Important APIs/types/functions: `lock_in_ptr_order(first, second)` returns guards in the same order as arguments.

Control flow: obtains raw Arc allocation pointers, asserts they differ, locks lower-address mutex first, then the other, and returns guards mapped to original argument order.

State/persistence: locks caller-owned mutexes; no storage.

Dependencies/integration: useful wherever pairs of shared objects must be mutated together.

Risks: raw pointer ordering is process-local and only prevents deadlocks when all callers use the same convention. Panics on poisoned mutexes and same mutex.

Test signals: unit tests cover both locks, reverse argument order, mutation, and same-mutex panic.
