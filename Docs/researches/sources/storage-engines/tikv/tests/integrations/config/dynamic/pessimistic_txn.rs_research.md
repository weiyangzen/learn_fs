# sources/storage-engines/tikv/tests/integrations/config/dynamic/pessimistic_txn.rs

## sources/storage-engines/tikv/tests/integrations/config/dynamic/pessimistic_txn.rs

Purpose: validates online config behavior for the pessimistic transaction lock manager.

Important APIs: `server::lock_manager::Config`, `LockManager`, `WaiterMgrScheduler`, `DetectorScheduler`, `LockManager::config_manager`, storage dynamic config atomics, `ConfigController`, and `Module::PessimisticTxn`.

Control flow: `setup` creates and starts a `LockManager` with `TestPdClient`, mock store address resolver, and `SecurityManager`, captures waiter/deadlock schedulers, then registers the lock manager config manager. Validation helpers send scheduler closures and wait on channels. The main test sets known defaults, confirms unrelated raftstore updates are ignored, changes wait-for-lock timeout and observes both waiter timeout and deadlock TTL, then toggles pipelined/in-memory locking, wake-up delay, and in-memory size limits through atomic dynamic configs.

State and persistence: all state is runtime lock-manager state, stored in schedulers and atomic fields. No file persistence occurs; the manager is stopped at the end.

Dependencies and integration points: security setup, PD test client, lock manager wait/deadlock workers, storage dynamic config consumers. Risks include async worker start/validation races and needing exact default constants. Test signals are timeout/TTL equality and atomic values after each `update_config`.
