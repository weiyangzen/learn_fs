# sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_generator.h

Purpose: declares the random workload generator that builds valid, dependency-aware `kv_workload` instances for model-vs-WiredTiger testing.

Important APIs and types: `kv_timing_stress_spec` holds weighted timing stress options and a `total` function. `kv_workload_generator_spec` holds probabilities and bounds for disaggregated mode, tables, sequences, concurrent transactions, record/value ranges, table type, timestamp usage, logging, operation mixes, existing-key choices, prepared transaction behavior, rollback choices, and timing stress. `kv_workload_generator::generate`, `generate_stress_configurations`, and `generate_log_configurations` are the public factories.

Control flow: construction stores a spec, seed, random engine, table contexts, and sequence list. `run()` creates tables and operation sequences, assigns dependencies, traverses them through `sequence_traversal`, assigns timestamps, and flattens runnable operations into a `kv_workload`. `sequence_traversal` tracks per-sequence dependency counts, runnable queues, and optional barriers such as timestamp assignment boundaries.

State and persistence: generator state is transient but models future database state through `table_context`, which records table IDs, names, formats, type, known keys, and operation counts. Key state steers selection of existing keys and removal/update effects so later generated operations stay meaningful. The produced workload may create durable WT effects when executed.

Dependencies and integration: includes `kv_workload.h`, `kv_workload_sequence.h`, and `random.h`. It depends on table type from `kv_table`, `data_value` formats, and probability macros from `random.h`. The generated workload is then consumed by both runners and `verify_workload`.

Risks: probability weights and dependency traversal must avoid invalid schedules, deadlocks, or timestamp regressions. `sequence_state` stores raw pointers under an assumption of non-concurrent traversal. Existing-key tracking is approximate relative to WT rollback/conflict behavior. Configuration strings generated for timing stress and logging must remain compatible with WT config syntax.

Test signals: useful tests check deterministic generation for a seed, validity via `kv_workload::verify`, successful model/WT return-code agreement, and coverage of prepared, rollback, crash, checkpoint, RTS, row, column, logged, and disaggregated cases.
