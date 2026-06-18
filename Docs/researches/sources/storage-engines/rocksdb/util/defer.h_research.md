# sources/storage-engines/rocksdb/util/defer.h

Purpose: RAII utilities for deferred scope cleanup and temporary value restoration.

Important types: `Defer` stores a `std::function<void()>` and invokes it in the destructor. `SaveAndRestore<T>` stores a pointer and saved value, optionally assigns a temporary new value, and restores the saved value in the destructor.

Control flow: construction captures cleanup/restoration state; destruction performs the action. Copying is deleted for both types to avoid duplicate cleanup or restoration.

State and persistence: state is process-local RAII state (`fn_`, `obj_`, `saved_`). There is no persistence. `SaveAndRestore` uses move semantics for saved values and restore assignment.

Dependencies and integration: includes `<functional>`, namespace header, and is used wherever RocksDB wants centralized cleanup around early returns or temporary overrides.

Risks: `Defer` destructor invokes user code and is not marked `noexcept`; throwing during stack unwinding would terminate. `SaveAndRestore` requires the pointed object to outlive the guard and be assignable. It is not thread-safe by itself.

Test signals: `defer_test.cc` covers block/function scope execution and basic save/restore.
