# sources/storage-engines/rocksdb/monitoring/thread_status_updater.cc

Purpose: Implements the low-level thread-local status tracker used to collect active thread information for `GetThreadList`.

Important APIs/types/functions: `RegisterThread`, `UnregisterThread`, `ResetThreadStatus`, `SetEnableTracking`, `SetColumnFamilyInfoKey`, operation/state setters, operation property setters, `SetOperationStartTime`, `GetThreadList`, `GetLocalThreadStatus`, `NewColumnFamilyInfo`, `EraseColumnFamilyInfo`, and `EraseDatabaseInfo`.

Control flow: Register lazily allocates thread-local `ThreadStatusData`, initializes type/id, and inserts it into the global active set under `thread_list_mutex_`. Setters mutate thread-local atomics only when tracking is enabled. `GetThreadList` locks the global maps, loads high-level fields first, then lower-level operation/state fields only if higher-level CF and operation information are valid, preserving consistency under lock-free updates.

State and dependencies: State includes thread-local `ThreadStatusData*`, global active thread set, CF info map, DB-to-CF key map, and a mutex. Disabled builds provide no-op setters and `GetThreadList` returns `NotSupported`.

Risks/test signals: Thread registration owns a raw heap allocation that must be released by `UnregisterThread`. Operation property indexes are not range-checked here. Comments define the high-to-low consistency contract. Debug verification exists in `thread_status_updater_debug.cc`.
