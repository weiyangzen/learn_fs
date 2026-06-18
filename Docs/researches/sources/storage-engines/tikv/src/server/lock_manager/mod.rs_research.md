# sources/storage-engines/tikv/src/server/lock_manager/mod.rs

Purpose: top-level server lock manager that wires the waiter manager and deadlock detector workers and implements the storage `LockManager` trait.

Important APIs/types/functions: `LockManager::new`, `start`, `stop`, worker start/stop helpers, `register_detector_role_change_observer`, `deadlock_service`, `config_manager`, `get_storage_dynamic_configs`, and trait methods `allocate_token`, `wait_for`, `update_wait_for`, `remove_lock_wait`, `has_waiter`, `dump_wait_for_entries`.

Control flow: construction creates two `FutureWorker`s and schedulers plus shared atomics. `start` launches the waiter manager and detector; `stop` joins both workers while ignoring join failures. `wait_for` converts no-timeout waits into immediate `KeyIsLocked`, otherwise increments `waiter_count`, schedules waiter registration, and schedules deadlock detection unless this is the transaction's first lock.

State and persistence: worker handles exist only on the owning instance; clones keep schedulers and shared atomics but not worker handles. Token allocation is an atomic counter. Wait state is in the waiter manager; detect graph is in the detector; no state is persisted.

Dependencies and integration: bridges storage lock-manager traits to server implementations, depends on PD, security, raftstore coprocessor host, storage dynamic configs, and lock diagnostic/wait types.

Risks: `waiter_count` is incremented before waiter manager processing to avoid lost wakeups, so scheduling failure paths must decrement through waiter-manager behavior or callback handling. First-lock detection bypass is a correctness/performance assumption for pessimistic transactions. Clones cannot start/stop workers.

Test signals: integration-style unit tests cover timeout, removal, deadlock reporting, first-lock no-detect behavior, no-timeout immediate failure, and clone benchmark.
