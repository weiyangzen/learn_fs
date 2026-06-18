# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_generator.cpp

Purpose: random workload generator that creates serial-equivalent transaction/special-operation sequences, derives dependencies, assigns valid timestamps, and emits a randomized interleaving for model/WT execution.

Important APIs and functions: default specs set probabilities for table counts, transaction operations, special operations, key reuse, logging, prepared transactions, and timing stress. `table_context::choose_existing_key` picks tracked live keys. `sequence_traversal` maintains runnable sequences under dependency and optional barrier constraints. `assign_timestamps` fills placeholders for prepare/commit/durable/stable/oldest timestamps. `create_table` emits row or column table creation. `generate_transaction` creates transaction sequences with reads, writes, removes, truncates, prepare/commit/rollback, and optional commit timestamp setting. `run` orchestrates generation, dependency creation, timestamp assignment, interleaving, and final validation.

Control flow and state: generator tracks tables, live key sets, transaction IDs, sequence DAG, database config, and random state. Special operations create barriers; overlapping key ranges create ordering dependencies; RTS blocks all earlier/later sequences. Disaggregated mode disables unsupported column/RTS/prepared paths and enforces stable timestamps before checkpoints/closes.

Dependencies and integration: uses `kv_workload_generator.h`, workload operations, random wrapper, and model utility helpers. Tools/tests call static `generate` and stress/log config helpers.

Risks and test signals: dependency logic is central; missed overlap can produce WT rollbacks not represented in the serial model. Narrow supported data formats limit coverage. Generated workloads self-check with `kv_workload::verify`, and seed replay is the main debugging signal.
