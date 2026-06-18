# sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.cpp

Purpose: Implements the in-memory collection model's key-count operations.

Important APIs/types/functions: constructor stores immutable `name` and `id` and initializes `_key_count`. `get_key_count` returns the atomic key count. `increase_key_count` atomically increments it.

Control flow: callers read key count before inserting contiguous new keys and increment only after commit.

State and persistence: key count is in-memory metadata mirroring persistent table contents; table contents are persisted elsewhere.

Dependencies/integration: used by `database` and workload operations to choose valid key ranges.

Risks and test signals: atomic increment does not alone prevent logical conflicts if multiple insertion threads extend the same collection concurrently; the header documents the expected single-threaded extension pattern.
