# sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner_wt.h

Purpose: declares the real WiredTiger runner for the workload language, including connection/session/cursor management and crash simulation support.

Important APIs and types: `kv_workload_runner_wt`, `k_config_base`, nested `session_context`, and C-compatible flexible `shared_state`. Public `run(const kv_workload &)` executes a workload in a WT home. Protected `do_operation` overloads implement every workload operation, plus `wiredtiger_open[_nolock]`, `wiredtiger_close[_nolock]`, `remove_local_files`, `add_table_uri`, `table_uri`, `allocate_txn_session`, `remove_txn_session`, and `txn_session`.

Control flow: `run` opens WT, prepares shared state, executes operations through `std::visit`, and records return codes. Table operations resolve workload table IDs to WT URIs. Transactional operations allocate per-transaction sessions, use cached cursors, and remove sessions at commit/rollback. Crash/checkpoint-crash use child/shared-state machinery so expected process death can be converted back into operation results and recovery can resume.

State and persistence: `_home` identifies the WT home. `_connection`, `_table_uris`, and `_sessions` are guarded by shared mutexes. `shared_state` stores crash index, expected crash flag, exception details, table URI states, database/connection/table config strings, and per-operation return codes across parent/child execution. Real persistence is WT data files in `_home`.

Dependencies and integration: includes `kv_workload.h`, `model/core.h`, and `wiredtiger.h`; it pairs with the implementation files outside this subset and is called by `kv_workload::run_in_wiredtiger` and `verify_workload`.

Risks: `shared_state` has fixed-size arrays and C strings (`tables[256]`, 256-byte configs/messages), so overlarge workloads/configs can overflow unless implementation bounds carefully. Cursor IDs assume 16 cursor slots per table. Correct lock discipline around connection/table/session maps is essential during restart/crash. Recovery must rebuild table URI state from shared memory accurately.

Test signals: `verify_workload` compares the WT runner return codes against the model runner, reopens the WT database, and verifies each table. Crash tests should exercise expected crash paths, recovery continuation, and correct preservation of table URI mappings and return-code prefixes.
