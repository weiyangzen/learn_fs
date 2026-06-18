# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.cc

- **Purpose:** Implements the factory function that selects the concrete lock manager for pessimistic transactions.
- **Important APIs/types/functions:** `NewLockManager(PessimisticTransactionDB* db, const TransactionDBOptions& opt)` returns a `std::shared_ptr<LockManager>`.
- **Control flow:** The function asserts a DB pointer. If `opt.lock_mgr_handle` is set, it aliases the handle-owned manager pointer into a shared pointer so the handle controls lifetime. Otherwise it chooses `PerKeyPointLockManager` when `use_per_key_point_lock_mgr` is true, or `PointLockManager` by default.
- **State and persistence behavior:** No persistent state is stored here. It determines the in-memory lock manager used by a transaction DB instance.
- **Dependencies:** Depends on the abstract lock manager header and point lock manager implementations.
- **Integration points:** Central construction point for TransactionDB pessimistic locking; callers should use it rather than directly instantiating implementations.
- **Risks:** The aliasing shared pointer for custom managers depends on `lock_mgr_handle` keeping the manager object valid. Range lock managers or external custom managers must be supplied through the handle path.
- **Test signals:** Tests should verify custom handle selection, per-key option selection, default point-lock selection, and lifetime of aliasing handles.
