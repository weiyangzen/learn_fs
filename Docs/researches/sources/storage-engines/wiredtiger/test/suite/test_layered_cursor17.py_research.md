# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor17.py

Purpose: scenario-driven coverage that follower cursor operations succeed on keys that exist only in the stable table, meaning they were written by the leader and checkpointed before the follower observed them.

Important APIs and functions: top-level wrappers `_op_reserve`, `_op_search`, `_op_search_near`, `_op_update`, `_op_remove`, and `_op_modify` normalize different cursor APIs to a return code. `test_layered_cursor17` uses `make_scenarios` to run one test body per operation, and uses `wiredtiger.Modify` for modify coverage.

Control flow: `insert_keys` writes ten timestamped keys on the leader. The leader sets the stable timestamp and checkpoints, the follower is opened and advanced to the checkpoint, and a follower cursor performs the parameterized operation on key `5` inside a transaction that is then rolled back.

State and persistence behavior: all target keys live only in the stable constituent; no follower ingest write is needed to make them visible. Update/remove/modify paths are validated for their ability to position and operate from stable data while the rollback prevents durable mutation of the test dataset.

Dependencies and integration: depends on disaggregated storage scenarios, follower checkpoint advance, layered cursor operation dispatch, and Python modify bindings. Risks include operation-specific code paths that only search ingest, stable-only positioned writes failing after a stable lookup, and `search_near` returning success but positioning incorrectly. Test signals are a single `0` return assertion for each operation scenario plus rollback cleanup.
