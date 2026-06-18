# Research: sources/storage-engines/rocksdb/include/rocksdb/user_write_callback.h

- **Purpose:** Exposes `UserWriteCallback`, a small interface for user-defined validation or side effects around writes.
- **Important APIs/types/functions:** `UserWriteCallback::Callback(DB*)` is the only operation and returns `Status`.
- **Control flow:** Internal write paths that accept a callback invoke `Callback()` with the target DB; the returned status can allow or abort the write flow depending on the caller.
- **State and persistence:** The interface has no state. Implementations may inspect DB state or maintain external state, but persistence semantics depend on the write path invoking it.
- **Dependencies:** Depends on `Status` and forward-declared `DB`.
- **Integration points:** Used by advanced write APIs or transaction paths that need user logic during a write.
- **Risks:** Callback implementations run in sensitive write-path context and must avoid deadlocks, expensive operations, and exceptions. The header does not define ownership or threading policy beyond the virtual contract.
- **Test signals:** Tests should cover callback success/failure propagation, DB pointer validity, write abort semantics, and callback behavior under concurrent writes.
