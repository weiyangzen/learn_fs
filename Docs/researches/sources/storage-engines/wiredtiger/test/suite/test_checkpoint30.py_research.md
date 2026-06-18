# sources/storage-engines/wiredtiger/test/suite/test_checkpoint30.py

Purpose: tests snapshot cursor visibility when aggregate time-window information says a page is visible but individual deleted on-disk versions are not all visible to an active reader.

Important APIs and types: timestamped transactions, long-lived reader transaction, `debug=(release_evict)` eviction cursor, `large_removes`, and `session.checkpoint`.

Control flow: write 100 rows at timestamp 10; hold open an uncommitted remove for key 1; remove the remaining keys at timestamp 20; start a reader transaction; commit key 1 remove at timestamp 25; verify the reader still sees key 1 before eviction, after eviction, and after checkpoint.

State and persistence behavior: the reader snapshot should not be invalidated by evicting or checkpointing pages whose aggregate deletion state may appear visible. The test protects per-key visibility when deletion state is persisted.

Dependencies and integration points: uses checkpoint, eviction, transaction snapshot isolation, and timestamped removes. Tiered storage is skipped.

Risks: the `check` helper ignores its `ts` parameter and relies on the session's existing transaction state for long-lived visibility. Data size is small but targets a subtle visibility edge.

Test signals: the reader sees exactly one row with `value_a` after each state transition.
