<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp22.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp22.py

Purpose: Randomly misuses timestamp APIs to confirm WiredTiger rejects invalid combinations without crashing, while preserving predictable global timestamp state and final row contents.

Important APIs/types/functions: `test_timestamp22` uses `suite_random`, `SimpleDataSet`, `make_scenarios`, a custom `expect` context manager, `updates`, `set_global_timestamps`, `expected_result_set_timestamp`, `prepare_transaction`, `timestamp_transaction`, `set_timestamp`, and stderr pattern handling.

Control flow: The randomizer runs 1,000 iterations normally or 100,000 in long-test mode. Each iteration may perform timestamped writes, prepared transactions, illegal durable/commit/read timestamp combinations, or global timestamp updates. The helper predicts whether each operation should succeed. It tracks `oldest_ts`, `stable_ts`, `last_commit_ts`, `last_durable`, and the last committed value, then validates final table contents.

State and persistence behavior: State is primarily in transaction metadata and global timestamp connection metadata. The test deliberately avoids cases that would panic the diagnostic suite after failed timestamp setting, then checks query_timestamp against the model after each global timestamp operation.

Dependencies and integration points: Broadly integrates transaction timestamp validation, prepared timestamp rules, global oldest/stable timestamp ordering, stderr cleanup, and row/column table formats.

Risks: Randomized tests can be hard to minimize, but the seed is printed. The expected-state model must track WiredTiger semantics closely or it can hide true engine regressions behind test-model mistakes.

Test signals: Every generated operation is wrapped in a success/failure expectation; final row verification ensures successful commits had the expected lasting effect.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp22.py -->
