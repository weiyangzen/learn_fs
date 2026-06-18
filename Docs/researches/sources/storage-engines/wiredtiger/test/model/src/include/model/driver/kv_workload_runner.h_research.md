# sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner.h

Purpose: declares and mostly defines the in-memory model runner for workload operations. It translates `operation::any` entries into calls on `kv_database`, `kv_table`, and `kv_transaction`.

Important APIs and types: `kv_workload_runner(kv_database &)`, `database()`, `run(const kv_workload &)`, and `run_operation(const operation::any &)`. Protected `do_operation` overloads handle every workload operation. Helpers `restart`, `add_table`, `table`, `add_transaction`, `remove_transaction`, and `transaction` manage runner-local ID maps.

Control flow: `run` iterates workload indexes, dispatching each variant through `std::visit`. Begin creates a model transaction and maps the workload transaction ID to it. Commit/rollback remove the transaction from the active map first, then finalize it. Create table creates a `kv_table`, infers table type from key/value formats, sets formats, and records workload table ID. Writes/read/truncate call table APIs. Restart/crash clear runner transaction state and call `kv_database::restart`; checkpoint, timestamps, and RTS call database APIs.

State and persistence: runner state is only workload ID mapping for tables and live transactions. Persistent modeled state lives in `kv_database`. The transaction and table maps are protected by `std::shared_mutex`; `restart` clears live transactions because WT sessions would not survive a restart.

Dependencies and integration: includes `kv_workload.h`, `kv_database.h`, `kv_table.h`, `kv_transaction.h`, and `wiredtiger.h` for return codes. It is the implementation behind `kv_workload::run`.

Risks: workload IDs must be unique and valid or model exceptions are thrown. `config` only understands `database`; `wt_config`, `evict`, `breakpoint`, and `nop` are no-ops in the model. `get` returns WT-style codes but currently ignores the returned value. Clearing transactions on restart may mask workload streams that incorrectly reference old transactions.

Test signals: compare model runner return-code vectors to WT runner vectors in `verify_workload`. Unit tests should check duplicate/missing table and transaction IDs, timestamp errors, restart/crash behavior, and that no-op WT-only operations do not affect model state.
