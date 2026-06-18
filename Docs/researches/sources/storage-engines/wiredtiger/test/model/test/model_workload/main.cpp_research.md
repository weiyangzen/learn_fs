# sources/storage-engines/wiredtiger/test/model/test/model_workload/main.cpp

## Purpose
This executable tests the workload abstraction used by the WiredTiger model test framework. It verifies that scripted workloads can be constructed, run in the model, run in WiredTiger, parsed from text, generated randomly, and replayed through debug-log verification.

## Important APIs, Types, and Functions
The file depends on `model::kv_workload`, `model::kv_workload_generator`, `model::operation::*`, `model::kv_database`, and verification helpers `verify_workload` and `verify_using_debug_log`. Scenario functions are `test_workload_basic`, `test_workload_txn`, `test_workload_prepared`, `test_workload_restart`, `test_workload_crash`, `test_workload_generator`, and `test_workload_parse`.

## Control Flow
Each workload scenario builds a `kv_workload` using chained `operator<<` calls with operations such as `create_table`, `begin_transaction`, `insert`, `remove`, `truncate`, `prepare_transaction`, `commit_transaction`, `checkpoint`, `checkpoint_crash`, `crash`, `restart`, `set_stable_timestamp`, and `rollback_to_stable`. The workload is first executed in an in-memory `kv_database`, expected final values are asserted, then `verify_workload` runs the same workload against WiredTiger in a scenario-specific home directory. Parser tests stringify operations, parse them back, and compare operation equality.

## State, Persistence, and Integration
The tests cover non-timestamped updates, timestamped transactions, prepared transaction durable timestamps, rollback-to-stable, restart and crash persistence, checkpoint crash markers, and generated workloads. The generator test retries known issue workloads up to a bound and disables disaggregated storage in its spec because verification currently needs special handling. Parser coverage includes quoted strings, escapes, whitespace, hex integers, optional arguments, unsigned numeric keys/values, and operation equality.

## Risks and Test Signals
The workload layer is a central integration point between generated model operations and the WT runner. Risks include parser/stringifier drift, generated invalid workloads, mismatched operation return-code semantics, and missing debug-log representation for workload operations. Signals are final model value assertions, `verify_workload` model-vs-WT verification, debug-log replay after each concrete workload, bounded retries for known generator issues, and parser round-trip equality.
