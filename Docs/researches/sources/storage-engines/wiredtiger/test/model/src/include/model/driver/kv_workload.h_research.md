# sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload.h

Purpose: defines the serializable workload language used to drive both the in-memory model and real WiredTiger. It gives tests a common operation stream for table creation, transaction lifecycle, timestamp control, checkpoint/crash/restart, and key-value operations.

Important APIs and types: `table_id_t`; mixins `with_txn_id`, `without_txn_id`, `with_table_id`, `without_table_id`; operation structs `begin_transaction`, `breakpoint`, `checkpoint`, `checkpoint_crash`, `commit_transaction`, `config`, `crash`, `create_table`, `evict`, `get`, `insert`, `nop`, `prepare_transaction`, `remove`, `restart`, `rollback_to_stable`, `rollback_transaction`, `set_commit_timestamp`, `set_oldest_timestamp`, `set_stable_timestamp`, `truncate`, and `wt_config`; `operation::any` as a `std::variant`; helpers `parse`, `transactional`, `transaction_id`, `table_op`, `table_id`; `kv_workload_operation`; and `kv_workload`.

Control flow: workload construction appends or prepends operations into an internal `std::deque`. Printing uses `std::visit` over the variant and per-operation `operator<<` overloads. Execution flows through `kv_workload::run(kv_database &)`, which delegates to the model runner, or `run_in_wiredtiger`, which delegates to the WT runner. `verify` checks stream validity before execution; `verify_noexcept` converts exceptions into boolean failure.

State and persistence: `kv_workload` is only an operation sequence and source sequence metadata; it does not own persistent data. Persistence effects are encoded by operations such as checkpoint, timestamp setting, rollback-to-stable, crash, restart, and transactional writes, then realized by the runners.

Dependencies and integration: includes `model/core.h`, `model/data_value.h`, `model/kv_database.h`, and `model/util.h`. It is consumed by `kv_workload_generator`, `kv_workload_runner`, `kv_workload_runner_wt`, and test helpers such as `verify_workload`.

Risks: adding an operation requires updating the variant, printer/parser, both runners, generator logic if applicable, and verification rules. `operation::table_id` throws if called on non-table operations. `get` operations intentionally do not encode expected values, and the model runner has a FIXME to use read values. Equality methods for stateless operations ignore the unused parameter by returning true.

Test signals: workload tests can compare return-code vectors from model and WT execution. The stream printer/parser is testable through round trips, while `verify_noexcept` offers quick rejection for invalid transaction/table ordering and timestamp ordering.
