# sources/storage-engines/wiredtiger/test/suite/test_layered_delta02.py

Purpose: constructs long delta chains and validates follower reconstruction for both explicit `layered:` tables and shared disaggregated `table:` objects with `block_manager=disagg`.

Important APIs and functions: `test_layered_delta02` uses `@disagg_test_class`, `precise_checkpoint=true`, `make_scenarios` over `layered` and `shared` prefixes, timestamped updates, repeated `conn.set_timestamp`, `session.checkpoint`, follower `wiredtiger_open`, and `disagg_advance_checkpoint`.

Control flow: the test creates the table, inserts 500 records at timestamp 100, checkpoints, then updates one key ten times at consecutive timestamps, advancing stable timestamp and checkpointing after each update. A follower is opened and advanced, then every key is read; the updated key must have the tenth value and all other keys must retain the base value.

State and persistence behavior: the key under test accumulates a chain of page deltas across multiple checkpoints. Follower reads validate that page-log delta chain traversal applies the latest update and does not affect unrelated rows.

Dependencies and integration: depends on disaggregated block manager configuration, precise checkpoints, layered and non-layered URI paths, and follower checkpoint synchronization. Risks include exceeding max delta chain assumptions, broken chain ordering, lost base image rows, or differences between layered and shared table handling. Test signals are full-table value equality after follower reconstruction.
