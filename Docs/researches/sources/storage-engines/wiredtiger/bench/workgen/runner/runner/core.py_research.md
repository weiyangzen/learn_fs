<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/core.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/core.py

Purpose: core helper library that lets Workgen Python runner scripts emulate common wtperf features: transactions, timed phases, extension config, multi-table expansion, log-like operations, grouped transactions, and range-partitioned populate.

Important APIs and functions: public helpers include `txn`, `sleep`, `timed`, `extensions_config`, `op_copy`, `op_append`, `op_multi_table`, `op_log_like`, `op_group_transaction`, and `op_populate_with_range`. Internal helpers include `_wiredtiger_builddir`, `_choose_pareto`, `_op_get_group_list`, `_op_copy_mod`, `_op_multi_table_as_list`, `_check_pareto`, `_op_log_op`, `_optype_is_write`, and `_op_transaction_list`.

Control flow: `txn` attaches a `Transaction` object to an operation. `timed` wraps operations in an `OpList` if needed and sets `_timed`. `extensions_config` finds exactly one matching shared library per extension and builds a WT config string. `op_multi_table` deep-copies operations across tables, with special Pareto/range-partition logic. `op_log_like` injects secondary log-table inserts for write-like operations. `op_group_transaction` restructures operation lists into transaction groups. `op_populate_with_range` maps initial inserts across fully and partially filled tables.

State and persistence: mutates Workgen operation objects, including private SWIG-backed fields. It does not write persistent storage directly.

Dependencies and integration: imports `Key`, `Operation`, `OpList`, `Table`, `Transaction`, and `Value` from Workgen. Used by most runner scripts.

Risks: relies on Workgen private attributes like `_group`, `_table`, `_key`, and `_repeatgroup`; SWIG/API changes can break it. `op_group_transaction` compares `ops_arg != Operation.OP_NONE`, which appears suspicious because `ops_arg` is an object, not an optype. Transaction plus Pareto range partition is explicitly unsupported. Random prime selection makes some expanded operation order nondeterministic.

Test signals: behavior is indirectly tested by all runner workloads; failures appear as operation construction exceptions, Workgen run errors, or distribution anomalies.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/core.py -->
