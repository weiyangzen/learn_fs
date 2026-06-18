# sources/storage-engines/rocksdb/monitoring/thread_status_updater.h

Purpose: Declares the internal structures and updater class that hold per-thread RocksDB status and global column-family metadata.

Important APIs/types/functions: `ConstantColumnFamilyInfo` stores DB key/name and CF name. `ThreadStatusData` stores atomics for enable flag, thread id/type, CF key, operation type, operation start time/stage/properties, and state. `ThreadStatusUpdater` exposes registration, status setters, `GetThreadList`, CF metadata map updates, and debug verification.

Control flow/integration: Most DB code should call `ThreadStatusUtil` rather than this class directly. The header documents the consistency rule: resets clear low-level fields first, sets update high-level fields first, and readers fetch high-to-low so partial results remain coherent.

State and dependencies: In enabled builds, `thread_status_data_` is thread-local; global maps and active data set are protected by `thread_list_mutex_`. Depends on `rocksdb/thread_status.h`, `rocksdb/status.h`, and `util/thread_operation.h`.

Risks/test signals: Raw pointers are used as DB/CF identity keys, so lifecycle map erasure is important. `enable_tracking` gates most updates. Disabled builds remove all real fields and behavior.
